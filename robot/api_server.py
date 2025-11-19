"""
FastAPI server for visualizing robot navigation in real-time.

Uses WebSocket for bidirectional communication:
- Server → Client: Robot state updates (10 Hz)
- Client → Server: Commands (set_target, start, stop)
"""

import asyncio
import json
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motors.motor_controller import MotorController

from geometry import GlobalCoordinate, GlobalPose
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
        self.pose = GlobalPose(GlobalCoordinate(0.0, 0.0), 0.0)
        self.target: Optional[GlobalCoordinate] = GlobalCoordinate(100, 100)
        self.obstacles: list[dict] = []
        self.is_running = True
        self.motor_speeds = {"left": 0, "right": 0}  # Current motor speeds


robot_state = RobotState()
motor_controller: Optional[MotorController] = None


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
                # Update obstacles from sensors
                hit_points = get_ultrasonic_hit_points()
                robot_state.obstacles = [
                    {"x": point.x, "y": point.y} for point in hit_points
                ]

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
                    if motor_controller:
                        motor_controller.stop()
                    print("Robot stopped")
                    await websocket.send_json(
                        {"type": "command_ack", "command": "stop"}
                    )

                elif command_type == "set_motor":
                    motor_data = data.get("data", {})
                    motor = motor_data.get("motor")  # "left", "right", or "both"
                    speed = motor_data.get("speed", 0)

                    if motor_controller:
                        if motor == "left":
                            motor_controller.set_left_motor(speed)
                            robot_state.motor_speeds["left"] = speed
                        elif motor == "right":
                            motor_controller.set_right_motor(speed)
                            robot_state.motor_speeds["right"] = speed
                        elif motor == "both":
                            left_speed = motor_data.get("left_speed", speed)
                            right_speed = motor_data.get("right_speed", speed)
                            motor_controller.set_both_motors(left_speed, right_speed)
                            robot_state.motor_speeds["left"] = left_speed
                            robot_state.motor_speeds["right"] = right_speed

                        print(f"Motor {motor} set")
                        await websocket.send_json(
                            {"type": "command_ack", "command": "set_motor"}
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "message": "Motor controller not connected",
                            }
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
        if motor_controller:
            motor_controller.stop()
            robot_state.motor_speeds = {"left": 0, "right": 0}


# --- Background Tasks (Simulation) ---


@app.on_event("startup")
async def startup_event():
    """Start background tasks when server starts"""
    global motor_controller

    # Try to connect to motor controller
    motor_controller = MotorController()
    if motor_controller.connect():
        print("Motor controller connected successfully")
    else:
        print("Running without motor controller (simulation mode)")
        motor_controller = None


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up when server shuts down"""
    global motor_controller
    if motor_controller:
        motor_controller.disconnect()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
