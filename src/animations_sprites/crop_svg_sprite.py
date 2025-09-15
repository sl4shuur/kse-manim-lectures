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


def path_points_from_d(d: str):
    """
    Extract control points from path 'd'. Handles M/L/H/V/C/Q/S/T (abs/rel).
    For curves we include control points and end points to over-approximate bbox.
    """
    if not d:
        return []

    tokens = re.findall(r"([MmLlHhVvCcQqSsTtZz])|([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)", d)
    points = []
    current_pos = (0.0, 0.0)

    command_groups = []
    current_command = None
    current_numbers = []

    for cmd_flag, number in tokens:
        if cmd_flag:
            if current_command and current_numbers:
                command_groups.append((current_command, current_numbers))
            current_command = cmd_flag
            current_numbers = []
        elif number:
            current_numbers.append(float(number))

    if current_command and current_numbers:
        command_groups.append((current_command, current_numbers))

    def add_point(x, y, relative=False):
        nonlocal current_pos
        if relative:
            current_pos = (current_pos[0] + x, current_pos[1] + y)
        else:
            current_pos = (x, y)
        points.append(current_pos)

    for command, numbers in command_groups:
        if not command:
            continue

        is_rel = command.islower()
        cmd = command.upper()
        vals = numbers
        i = 0

        while i < len(vals):
            if cmd in ("M", "L", "T") and i + 1 < len(vals):
                add_point(vals[i], vals[i + 1], relative=is_rel)
                i += 2
            elif cmd == "H" and i < len(vals):
                add_point(vals[i], current_pos[1], relative=is_rel)
                i += 1
            elif cmd == "V" and i < len(vals):
                add_point(current_pos[0], vals[i], relative=is_rel)
                i += 1
            elif cmd == "C" and i + 5 < len(vals):
                if is_rel:
                    points.extend(
                        [
                            (current_pos[0] + vals[i], current_pos[1] + vals[i + 1]),
                            (
                                current_pos[0] + vals[i + 2],
                                current_pos[1] + vals[i + 3],
                            ),
                        ]
                    )
                    add_point(vals[i + 4], vals[i + 5], relative=True)
                else:
                    points.extend([(vals[i], vals[i + 1]), (vals[i + 2], vals[i + 3])])
                    add_point(vals[i + 4], vals[i + 5], relative=False)
                i += 6
            elif cmd in ("Q", "S") and i + 3 < len(vals):
                if is_rel:
                    points.append(
                        (current_pos[0] + vals[i], current_pos[1] + vals[i + 1])
                    )
                    add_point(vals[i + 2], vals[i + 3], relative=True)
                else:
                    points.append((vals[i], vals[i + 1]))
                    add_point(vals[i + 2], vals[i + 3], relative=False)
                i += 4
            else:
                break

    return points


def bbox_of_path_d(d: str, transform_matrix):
    """Compute a path bbox after applying the transform matrix."""
    points = path_points_from_d(d)
    if not points:
        return None
    transformed = [apply_mat(transform_matrix, x, y) for x, y in points]
    xs, ys = zip(*transformed)
    return (min(xs), min(ys), max(xs), max(ys))


def build_id_map(defs: ET.Element) -> dict[str, ET.Element]:
    """Build id -> element map for <defs> symbols/groups."""
    id_map = {}
    if defs is None:
        return id_map
    for element in defs.iter():
        element_id = element.attrib.get("id")
        if element_id:
            id_map[element_id] = element
    return id_map


def calculate_bbox_recursive(
    element: ET.Element, parent_matrix, id_map
) -> tuple | None:
    """
    Recursively compute a bbox for an element considering transforms.
    Supports <g>, <use>, and <path>.
    """
    bbox = None
    name = tagn(element)

    if name == "g":
        local = mat_mul(parent_matrix, mat_from_transform(element.get("transform", "")))
        for child in element:
            child_bbox = calculate_bbox_recursive(child, local, id_map)
            bbox = bbox_union(bbox, child_bbox)

    elif name == "use":
        href = element.attrib.get(f"{{{XLINK_NS}}}href")
        if href and href.startswith("#"):
            target = id_map.get(href[1:])
            if target is not None:
                local = mat_mul(
                    parent_matrix, mat_from_transform(element.get("transform", ""))
                )
                bbox = calculate_bbox_recursive(target, local, id_map)

    elif name == "path":
        local = mat_mul(parent_matrix, mat_from_transform(element.get("transform", "")))
        bbox = bbox_of_path_d(element.get("d", ""), local)

    return bbox
