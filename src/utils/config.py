from pathlib import Path

# Base of the project
BASE_DIR = Path(__file__).parent.parent.parent
SOURCES_DIR = BASE_DIR / "src"

# Sub-folders for different assets
ASSETS_DIR = BASE_DIR / "assets"
SPRITES_SHEETS_DIR = ASSETS_DIR / "sprites_sheets"
SPRITES_POSES_DIR = ASSETS_DIR / "sprites_poses"
LOGOS_DIR = ASSETS_DIR / "logos"

SPRITE_ANIMATIONS_DIR = SOURCES_DIR / "animations_sprites"
LECTURE_ANIMATIONS_DIR = SOURCES_DIR / "animations_lectures"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"

# check if the directories exist, if not create them
for directory in [
    ASSETS_DIR,
    SPRITES_SHEETS_DIR,
    SPRITES_POSES_DIR,
    LOGOS_DIR,
    SPRITE_ANIMATIONS_DIR,
    LECTURE_ANIMATIONS_DIR,
    NOTEBOOKS_DIR,
]:
    if directory.exists() and directory.is_file():
        directory.unlink()  # Remove the file if a file exists with the same name
    directory.mkdir(parents=True, exist_ok=True)

POSE_PREFIX = "pose_"

# List of good poses for the character
POSES_NUM_LIST = ["01", "08", "09", "12", "13", "14", "15", "16", "19", "24"]

# Common virtual environment folder names
# please keep this list updated if you use a different name
# or use just .venv or venv (the most common ones)
VENV_NAMES = [
    ".venv",
    "venv",
    "env",
    "virtualenv",
    ".virtualenv",
    "manim_venv",
    ".manim_venv",
]