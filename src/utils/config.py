from pathlib import Path

# Base of the project
BASE_DIR = Path(__file__).parent.parent.parent

# Sub-folders for different assets
ASSETS_DIR = BASE_DIR / "assets"
SPRITES_SHEETS_DIR = ASSETS_DIR / "sprites_sheets"
SPRITES_POSES_DIR = ASSETS_DIR / "sprites_poses"

# check if the directories exist, if not create them
for directory in [ASSETS_DIR, SPRITES_SHEETS_DIR, SPRITES_POSES_DIR]:
    if directory.exists() and directory.is_file():
        directory.unlink()  # Remove the file if a file exists with the same name
    directory.mkdir(parents=True, exist_ok=True)

POSE_PREFIX = "pose_"
POSES_NUM_LIST = ["01", "08", "09", "12", "13", "14", "15", "16", "19", "24"]
