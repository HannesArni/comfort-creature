"""
FastAPI server for visualizing robot navigation in real-time.

Uses WebSocket for bidirectional communication:
- Server → Client: Robot state updates (10 Hz)
- Client → Server: Commands (set_target, start, stop)
"""

import asyncio
import json
import math
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from geometry import GlobalCoordinate, GlobalPose
from utils.get_ultrasonic_hit_points import get_ultrasonic_hit_points

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
        self.target: Optional[GlobalCoordinate] = None
        self.obstacles: list[dict] = []
        self.is_running = False


robot_state = RobotState()


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
                            "x": robot_state.pose.coordinate.x,
                            "y": robot_state.pose.coordinate.y,
                            "heading": robot_state.pose.heading,
                        },
                        "target": (
                            {"x": robot_state.target.x, "y": robot_state.target.y}
                            if robot_state.target
                            else None
                        ),
                        "obstacles": robot_state.obstacles,
                        "is_running": robot_state.is_running,
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
                    print("Robot stopped")
                    await websocket.send_json(
                        {"type": "command_ack", "command": "stop"}
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


# --- Background Tasks (Simulation) ---


@app.on_event("startup")
async def startup_event():
    """Start background tasks when server starts"""
    asyncio.create_task(simulate_robot_movement())


async def simulate_robot_movement():
    """
    Simulate robot movement for testing.

    In production, this would be replaced with actual motor control
    and sensor integration.
    """
    await asyncio.sleep(1)  # Wait for server to fully start

    while True:
        if robot_state.is_running and robot_state.target:
            # Simple simulation: move toward target
            dx = robot_state.target.x - robot_state.pose.coordinate.x
            dy = robot_state.target.y - robot_state.pose.coordinate.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 1.0:  # Still moving
                # Update heading to face target
                robot_state.pose.heading = math.atan2(dx, dy)

                # Move forward at 10 cm/s
                speed = 10.0  # cm/s
                step = speed * 0.1  # 10 Hz update

                new_x = robot_state.pose.coordinate.x + (dx / distance) * step
                new_y = robot_state.pose.coordinate.y + (dy / distance) * step
                robot_state.pose = GlobalPose(
                    GlobalCoordinate(new_x, new_y), robot_state.pose.heading
                )
            else:
                # Reached target
                robot_state.is_running = False
                print("Target reached!")

        await asyncio.sleep(0.1)  # 10 Hz control loop


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
