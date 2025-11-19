"""
Serial protocol for handling Arduino communication.

Uses asyncio.Protocol pattern for non-blocking serial I/O.
Generic line-based protocol - delegates line processing to callback.
"""

import asyncio
from typing import Callable, Optional

import serial_asyncio  # type: ignore[import-not-found]


class SerialProtocol(asyncio.Protocol):
    """Generic serial protocol for line-based communication."""

    def __init__(self, on_line: Callable[[str], None]):
        """
        Initialize serial protocol.

        Args:
            on_line: Callback function called when a complete line is received
        """
        self.on_line = on_line
        self.transport: Optional[asyncio.Transport] = None
        self.buffer = bytearray()

    async def connect(self, port: str, baudrate: int) -> bool:
        """
        Establish serial connection.

        Args:
            port: Serial port path (e.g., "/dev/ttyUSB0")
            baudrate: Baud rate for serial communication

        Returns:
            True if connection successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await serial_asyncio.create_serial_connection(
                loop, lambda: self, port, baudrate=baudrate
            )

            # Wait for Arduino to reset
            await asyncio.sleep(2)
            print(f"Connected to Arduino on {port}")
            return True

        except Exception as e:
            print(f"Failed to connect to Arduino: {e}")
            return False

    def connection_made(self, transport):
        """Called when serial connection is established."""
        self.transport = transport
        print("Serial connection established")

    def data_received(self, data):
        """Called when data is received from serial port."""
        self.buffer.extend(data)

        # Process complete lines
        while b"\n" in self.buffer:
            line_bytes, self.buffer = self.buffer.split(b"\n", 1)
            try:
                line = line_bytes.decode("utf-8").rstrip()
                self._process_line(line)
            except UnicodeDecodeError as e:
                print(f"Error decoding serial data: {e}")

    def _process_line(self, line: str):
        """Process a complete line by calling the callback."""
        if line:
            self.on_line(line)

    def connection_lost(self, exc):
        """Called when serial connection is lost."""
        if exc:
            print(f"Serial connection lost: {exc}")
        else:
            print("Serial connection closed")

    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return self.transport is not None

    def send_command(self, command: str):
        """
        Send command to Arduino.

        Args:
            command: Command string (e.g., "left 255", "stop")
        """
        if not self.transport:
            print("Error: Not connected to Arduino")
            return

        try:
            self.transport.write(f"{command}\n".encode())
        except Exception as e:
            print(f"Error sending command '{command}': {e}")

    def close(self):
        """Close the serial connection."""
        if self.transport:
            self.transport.close()
