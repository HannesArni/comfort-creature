# Comfort Creature

An autonomous navigation system for robotic wheelchairs.

## Project Structure

- **`geometry/`** - Coordinate system types and spatial primitives for navigation
- **`utils/`** - Utility modules including ultrasonic-based obstacle avoidance

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or on Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the code:**
   ```bash
   python main.py
   ```

## Development

**Linting and formatting:**
```bash
ruff check .          # Check for linting issues
ruff check . --fix    # Auto-fix issues
black .               # Format code
mypy .                # Type checking
```

## Getting Started

See the [coordinate system documentation](geometry/README.md) for details on how positions and headings are represented in this project.
