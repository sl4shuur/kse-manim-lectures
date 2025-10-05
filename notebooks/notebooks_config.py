from pathlib import Path
import sys

# Add parent directory to path
# root -> notebooks -> notebooks_config.py
# thus, we need to go up two levels to reach the project root
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from src.utils.config import UkrainianTexTemplate
from src.animations_sprites.ManimSprite import ManimSprite

if __name__ == "__main__":
    print("Project root added to sys.path:", project_root)
    print("UkrainianTeXTemplate:", UkrainianTexTemplate)
    print("ManimSprite:", ManimSprite)