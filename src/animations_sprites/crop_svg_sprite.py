from pathlib import Path
import xml.etree.ElementTree as ET

from src.utils.config import SPRITES_SHEETS_DIR, SPRITES_POSES_DIR

INPUT_FILE = Path(SPRITES_SHEETS_DIR) / "adventurer_vector.svg"
OUTPUT_DIR = Path(SPRITES_POSES_DIR)
PREFIX = "pose"


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)


def tag(local: str) -> str:
    return f"{{{SVG_NS}}}{local}"


def tagn(el: ET.Element) -> str:
    return el.tag.split("}")[-1]
