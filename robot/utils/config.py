import os
from os.path import dirname, join

from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv()

# Access variables
arduino_port = os.getenv("ARDUINO_PORT")
arduino_baud_rate = os.getenv("ARDUINO_BAUD_RATE")
