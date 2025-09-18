# KSE Manim Lectures

## Prerequisites

- **Python** installed on your system.
- **uv CLI** installed and on your `PATH` (see [Astral uv docs](https://docs.astral.sh/uv/)).

### How to install uv?

For all systems should work the following command:

```bash
pip install uv
```

See the [Astral uv docs](https://docs.astral.sh/uv/) for more installation options.

## How setup the project?

1. Clone the repository:

   ```bash
   git clone https://github.com/sl4shuur/kse-manim-lectures
   cd kse-manim-lectures
   ```

2. Sync the dependencies:

   ```bash
   uv sync
   ```

3. Run what you want using `uv run <script>` command.

   For example to run the animated sprites example:

   ```bash
   uv run src/animations_sprites/animated_sprites.py
   ```

   or directly with Python:

   ```bash
   # Activate your virtual environment first
   # (Windows)
   .venv\Scripts\Activate

   # (macOS/Linux)
   source .venv/bin/activate

   # Run the script
   python src/animations_sprites/animated_sprites.py
   ```
