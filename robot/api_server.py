"""
FastAPI server for visualizing robot navigation in real-time.

Uses WebSocket for bidirectional communication:
- Server → Client: Robot state updates (10 Hz)
- Client → Server: Commands (set_target, start, stop)
"""

import asyncio
import json
from dataclasses import asdict
from typing import Optional

from camera.get_target_from_camera import get_target_from_camera, CameraTarget
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motors.motor_controller import MotorController

from geometry import GlobalCoordinate, GlobalPose
from utils.constants import MotorSide
from utils.get_ultrasonic_hit_points import get_ultrasonic_hit_points, sensors

app = FastAPI(title="Comfort Creature Visualizer")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- State Management ---


class RobotState:
    """Current state of the robot"""

    def __init__(self):
        self.pose = GlobalPose(GlobalCoordinate(900.0, 100.0), 0.0)
        # self.target: Optional[GlobalCoordinate] = GlobalCoordinate(000, 500)
        self.target: Optional[GlobalCoordinate] = None
        self.is_target_facing_camera = False
        self.obstacles: list[dict] = []
        self.is_running = True
        self.motor_speeds = {"left": 0, "right": 0}  # Current motor speeds


robot_state = RobotState()
motor_controller = MotorController()


# --- REST Endpoints (minimal, just health check) ---


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Comfort Creature API"}


# --- WebSocket Endpoint ---


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional communication.

    Server → Client: State updates at 10 Hz
    Client → Server: Commands (set_target, start, stop)

    Message format from client:
    {
        "type": "set_target",
        "data": {"x": 100.0, "y": 200.0}
    }
    {
        "type": "start"
    }
    {
        "type": "stop"
    }
    """
    await websocket.accept()
    print("WebSocket client connected")

    # Task for sending state updates
    async def send_state_updates():
        try:
            while True:
                # Update pose from motor controller
                if motor_controller.is_connected():
                    robot_state.pose = motor_controller.pose

                # Update obstacles from sensors
                hit_points = get_ultrasonic_hit_points()
                robot_state.obstacles = [
                    {"x": point.x, "y": point.y} for point in hit_points
                ]

                # Get PID data from motors if available
                pid_data = None
                if motor_controller.is_connected():
                    pid_data = {
                        "left": asdict(
                            motor_controller.motors[MotorSide.LEFT].get_pid_state()
                        ),
                        "right": asdict(
                            motor_controller.motors[MotorSide.RIGHT].get_pid_state()
                        ),
                    }

                # Prepare state update
                state = {
                    "type": "state_update",
                    "data": {
                        "pose": {
                            "position": {
                                "x": robot_state.pose.position.x,
                                "y": robot_state.pose.position.y,
                            },
                            "heading": robot_state.pose.heading,
                        },
                        "target": (
                            {"x": robot_state.target.x, "y": robot_state.target.y}
                            if robot_state.target
                            else None
                        ),
                        "obstacles": robot_state.obstacles,
                        "is_running": robot_state.is_running,
                        "motor_speeds": robot_state.motor_speeds,
                        "pid_data": pid_data,
                        "in_automatic_mode": (motor_controller.in_automatic_mode),
                        "sensors": [
                            {
                                "pose": {
                                    "position": {
                                        "x": sensor.pose.position.x,
                                        "y": sensor.pose.position.y,
                                    },
                                    "heading": sensor.pose.heading,
                                },
                                "name": sensor.name,
                            }
                            for sensor in sensors
                        ],
                    },
                }

                await websocket.send_json(state)
                await asyncio.sleep(0.1)  # 10 Hz update rate

        except Exception as e:
            print(f"Error sending state updates: {e}")

    # Task for receiving commands
    async def receive_commands():
        try:
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)

                command_type = data.get("type")

                if command_type == "set_target":
                    target_data = data.get("data", {})
                    x = target_data.get("x")
                    y = target_data.get("y")
                    if x is not None and y is not None:
                        robot_state.target = GlobalCoordinate(x, y)
                        print(f"Target set to ({x}, {y})")
                        await websocket.send_json(
                            {"type": "command_ack", "command": "set_target"}
                        )

                elif command_type == "start":
                    robot_state.is_running = True
                    print("Robot started")
                    await websocket.send_json(
                        {"type": "command_ack", "command": "start"}
                    )

                elif command_type == "stop":
                    robot_state.is_running = False
                    await motor_controller.stop()
                    print("Robot stopped")
                    await websocket.send_json(
                        {"type": "command_ack", "command": "stop"}
                    )

                elif command_type == "set_motor":
                    motor_data = data.get("data", {})
                    motor = motor_data.get("motor")  # "left", "right", or "both"
                    speed = motor_data.get("speed", 0)

                    if motor == "left":
                        await motor_controller.set_motor(MotorSide.LEFT, speed)
                    elif motor == "right":
                        await motor_controller.set_motor(MotorSide.RIGHT, speed)
                    elif motor == "both":
                        await motor_controller.set_motor(
                            MotorSide.LEFT, motor_data.get("left_speed", 0)
                        )
                        await motor_controller.set_motor(
                            MotorSide.RIGHT, motor_data.get("right_speed", 0)
                        )

                    print(f"Motor {motor} set", speed)
                    await websocket.send_json(
                        {"type": "command_ack", "command": "set_motor"}
                    )

                elif command_type == "set_automatic_mode":
                    mode_data = data.get("data", {})
                    automatic_mode = mode_data.get("enabled", False)

                    motor_controller.in_automatic_mode = automatic_mode
                    if not automatic_mode:
                        await motor_controller.stop()
                    print(f"Automatic mode set to: {automatic_mode}")
                    await websocket.send_json(
                        {"type": "command_ack", "command": "set_automatic_mode"}
                    )

                else:
                    print(f"Unknown command type: {command_type}")
                    await websocket.send_json(
                        {"type": "error", "message": f"Unknown command: {command_type}"}
                    )

        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print(f"Error receiving commands: {e}")

    # Run both tasks concurrently
    try:
        await asyncio.gather(send_state_updates(), receive_commands())
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
        # Stop motors on disconnect for safety
        await motor_controller.stop()
        robot_state.motor_speeds = {"left": 0, "right": 0}


control_loop_task: Optional[asyncio.Task[None]] = None
camera_loop_task: Optional[asyncio.Task[None]] = None


# --- Background Tasks (Simulation) ---
async def camera_target_loop() -> None:
    """Main navigation/control loop running continuously"""
    loop = asyncio.get_event_loop()
    while True:
        if not motor_controller.in_automatic_mode:
            await asyncio.sleep(0.1)
            continue
        target: Optional[CameraTarget] = None
        target = await loop.run_in_executor(None, get_target_from_camera)
        if target:
            robot_state.target = target.coordinate.to_global(robot_state.pose)
            robot_state.is_target_facing_camera = target.is_facing_camera
        else:
            robot_state.target = None


async def control_loop():
    """Main navigation/control loop running continuously"""
    while True:
        try:
            if motor_controller.is_connected():
                # Run automatic control if enabled
                await motor_controller.target_count_test(
                    robot_state.target, robot_state.is_target_facing_camera
                )

            await asyncio.sleep(0.05)  # 50 Hz control rate
        except Exception as e:
            print(f"Control loop error: {e}")
            await asyncio.sleep(1)  # Back off on error


@app.on_event("startup")
async def startup_event():
    """Start background tasks when server starts"""
    global motor_controller

    # Try to connect to motor controller
    motor_controller = MotorController()
    if await motor_controller.connect():
        print("Motor controller connected successfully")
    else:
        print("Running without motor controller (simulation mode)")
        motor_controller = None

    global control_loop_task
    global camera_loop_task
    control_loop_task = asyncio.create_task(control_loop())
    camera_loop_task = asyncio.create_task(camera_target_loop())


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up when server shuts down"""
    global motor_controller
    motor_controller.disconnect()
    if control_loop_task:
        control_loop_task.cancel()
        try:
            await control_loop_task
        except asyncio.CancelledError:
            print("Control loop cancelled")
    if camera_loop_task:
        camera_loop_task.cancel()
        try:
            await camera_loop_task
        except asyncio.CancelledError:
            print("Control loop cancelled")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
