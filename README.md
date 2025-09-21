# KSE Manim Lectures

## Prerequisites (to use locally)

- **Python** installed on your system.
- **Docker** installed and running (for rendering scenes on your machine). See [Docker installation guide](https://docs.docker.com/get-docker/).
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

   For example to run the render (locally, via Docker) script

   ```bash
   uv run render.py
   ```

   or directly with Python:

   ```bash
   # Activate your virtual environment first
   # (Windows)
   .venv\Scripts\Activate

   # (macOS/Linux)
   source .venv/bin/activate

   # Run the script
   python render.py
   ```

## How to run the project on the cloud?

So in order to run the project on the cloud it is recommended to use [Binder](https://mybinder.org/).
You can use the following link to launch the project on Binder:

[![Open in Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sl4shuur/kse-manim-lectures/chore%2Fbinder-manim-setup?urlpath=lab/tree/notebooks/manim_sprites.ipynb)
