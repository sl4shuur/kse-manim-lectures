import re
import xml.etree.ElementTree as ET
from pathlib import Path

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


def mat_identity():
    """Return identity 2x3 affine matrix [a b c d e f]."""
    return [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]


def mat_mul(A, B):
    """Matrix multiply: A∘B (apply B first, then A)."""
    a1, b1, c1, d1, e1, f1 = A
    a2, b2, c2, d2, e2, f2 = B
    return [
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    ]


def mat_translate(tx, ty):
    """Translation matrix."""
    return [1.0, 0.0, 0.0, 1.0, float(tx), float(ty)]


def mat_from_transform(attr: str):
    """
    Parse `transform` attribute into a 2x3 matrix.
    Supports `translate(...)` and `matrix(...)` (add scale/rotate if needed).
    """
    M = mat_identity()
    if not attr:
        return M

    for match in re.finditer(r"(matrix|translate)\s*\(([^)]*)\)", attr):
        kind = match.group(1)
        args = [float(x) for x in re.split(r"[, \t]+", match.group(2).strip()) if x]
        if kind == "translate":
            tx = args[0] if args else 0.0
            ty = args[1] if len(args) > 1 else 0.0
            M = mat_mul(M, mat_translate(tx, ty))
        elif kind == "matrix" and len(args) == 6:
            M = mat_mul(M, args)
    return M


def apply_mat(M, x, y):
    """Apply 2x3 matrix to a point (x, y)."""
    a, b, c, d, e, f = M
    return (a * x + c * y + e, b * x + d * y + f)
