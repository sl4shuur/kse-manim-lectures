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

# Clustering sensitivity:
# Minimum absolute intersection area (px^2) to link two groups
MIN_INTERSECTION_AREA = 100
# Minimum intersection share vs. the smaller bbox to link two groups
MIN_INTERSECTION_PERCENT = 0.10


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


def bbox_union(A, B):
    """Union of two bboxes (x1, y1, x2, y2)."""
    if A is None:
        return B
    if B is None:
        return A
    return (min(A[0], B[0]), min(A[1], B[1]), max(A[2], B[2]), max(A[3], B[3]))


def bbox_area(bbox):
    """Area of bbox."""
    if bbox is None:
        return 0.0
    x1, y1, x2, y2 = bbox
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def bbox_intersection(A, B):
    """Intersection of two bboxes, or None if disjoint."""
    if A is None or B is None:
        return None
    ax1, ay1, ax2, ay2 = A
    bx1, by1, bx2, by2 = B
    x1 = max(ax1, bx1)
    y1 = max(ay1, by1)
    x2 = min(ax2, bx2)
    y2 = min(ay2, by2)
    if x1 >= x2 or y1 >= y2:
        return None
    return (x1, y1, x2, y2)


def should_cluster_together(bbox1, bbox2):
    """
    Decide if two bboxes should be linked in the same cluster.
    Requires both a minimum absolute area and a minimum relative share
    w.r.t. the smaller bbox.
    """
    inter = bbox_intersection(bbox1, bbox2)
    if inter is None:
        return False

    inter_area = bbox_area(inter)
    if inter_area < MIN_INTERSECTION_AREA:
        return False

    area1 = bbox_area(bbox1)
    area2 = bbox_area(bbox2)
    smaller = min(area1, area2)
    if smaller > 0:
        share = inter_area / smaller
        return share >= MIN_INTERSECTION_PERCENT
    return False
