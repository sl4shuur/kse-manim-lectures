from __future__ import annotations

import io
from pathlib import Path
from typing import List, Tuple, Iterable
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import cairosvg

from src.utils.config import SPRITES_SHEETS_DIR, SPRITES_POSES_DIR

INPUT_FILE = SPRITES_SHEETS_DIR / "player_vector.svg"
OUTPUT_DIR = SPRITES_POSES_DIR
PREFIX = "pose"

# Parameters
RASTER_SCALE = 1.0
INTERSECT_PAD = 1.0
EXPORT_MARGIN = 8.0
MIN_GROUPS_IN_POSE = 4
MIN_POSE_W, MIN_POSE_H = 20.0, 20.0

# Namespaces
NS_SVG = "http://www.w3.org/2000/svg"
NS_XLINK = "http://www.w3.org/1999/xlink"
ET.register_namespace("", NS_SVG)
ET.register_namespace("xlink", NS_XLINK)


def _localname(tag: str) -> str:
    """Return tag without namespace prefix."""
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def _parse_svg(svg_path: Path) -> ET.Element:
    """Parse SVG and return the root element."""
    return ET.parse(svg_path).getroot()


def _get_canvas_size(root: ET.Element) -> Tuple[float, float]:
    """Get canvas width/height from viewBox or width/height attributes."""
    vb = root.get("viewBox")
    if vb:
        _, _, w, h = map(float, vb.split())
        return w, h

    def _num(s: str | None) -> float:
        return float(str(s).replace("px", "")) if s else 1000.0

    return _num(root.get("width")), _num(root.get("height"))


def _collect_top_groups(root: ET.Element) -> List[Tuple[int, ET.Element]]:
    """Collect top-level <g> elements only."""
    return [
        (idx, child) for idx, child in enumerate(root) if _localname(child.tag) == "g"
    ]


def _build_svg_wrapper(
    children: Iterable[ET.Element],
    view_box: Tuple[float, float, float, float],
    copy_defs_from: ET.Element | None,
) -> str:
    """Wrap given children into a standalone SVG string."""
    x, y, w, h = view_box
    attrs = {
        "xmlns": NS_SVG,
        "xmlns:xlink": NS_XLINK,
        "viewBox": f"{x} {y} {w} {h}",
        "width": str(w),
        "height": str(h),
    }
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    parts = [f"<svg {attr_str}>"]

    if copy_defs_from is not None:
        defs = copy_defs_from.find(f".//{{{NS_SVG}}}defs")
        if defs is not None:
            parts.append(ET.tostring(defs, encoding="unicode"))

    parts.append("<g>")
    parts.extend(ET.tostring(el, encoding="unicode") for el in children)
    parts.append("</g></svg>")
    return "".join(parts)


def _build_single_group_svg(
    group: ET.Element,
    base_w: float,
    base_h: float,
    copy_defs_from: ET.Element | None,
) -> str:
    """Wrap one group into full-canvas SVG."""
    attrs = {
        "xmlns": NS_SVG,
        "xmlns:xlink": NS_XLINK,
        "viewBox": f"0 0 {base_w} {base_h}",
        "width": str(int(base_w)),
        "height": str(int(base_h)),
    }
    attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    parts = [f"<svg {attr_str}>"]

    if copy_defs_from is not None:
        defs = copy_defs_from.find(f".//{{{NS_SVG}}}defs")
        if defs is not None:
            parts.append(ET.tostring(defs, encoding="unicode"))

    parts.append(ET.tostring(group, encoding="unicode"))
    parts.append("</svg>")
    return "".join(parts)


def _raster_bbox_of_group(
    group: ET.Element,
    base_w: float,
    base_h: float,
    defs_root: ET.Element | None,
    scale: float = RASTER_SCALE,
    alpha_threshold: int = 1,
) -> Tuple[float, float, float, float] | None:
    """Rasterize a single <g> and compute visible bbox."""
    svg_str = _build_single_group_svg(group, base_w, base_h, defs_root)
    png_bytes = cairosvg.svg2png(
        bytestring=svg_str.encode("utf-8"),
        output_width=int(base_w * scale),
        output_height=int(base_h * scale),
    )

    if png_bytes is None:
        raise RuntimeError("cairosvg.svg2png returned None")

    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    alpha = np.array(img)[..., 3]
    ys, xs = np.where(alpha > alpha_threshold)
    if xs.size == 0:
        return None

    xmin_px, xmax_px = xs.min(), xs.max()
    ymin_px, ymax_px = ys.min(), ys.max()
    return (
        xmin_px / scale,
        ymin_px / scale,
        (xmax_px + 1) / scale,
        (ymax_px + 1) / scale,
    )


def _rects_intersect(
    a: Tuple[float, float, float, float],
    b: Tuple[float, float, float, float],
    pad: float = 0.0,
) -> bool:
    """Check if two rectangles intersect with optional padding."""
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    return not (
        ax1 <= bx0 - pad or bx1 <= ax0 - pad or ay1 <= by0 - pad or by1 <= ay0 - pad
    )


def _union_bbox(
    rects: List[Tuple[float, float, float, float]],
) -> Tuple[float, float, float, float]:
    """Compute union bbox for a list of rectangles."""
    xs = [coord for rect in rects for coord in (rect[0], rect[2])]
    ys = [coord for rect in rects for coord in (rect[1], rect[3])]
    return min(xs), min(ys), max(xs), max(ys)


def _cluster_groups_into_poses(
    groups: List[Tuple[int, ET.Element]],
    bboxes: List[Tuple[float, float, float, float]],
    pad: float = INTERSECT_PAD,
) -> List[List[int]]:
    """Build intersection graph and return connected components."""
    n = len(groups)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if _rects_intersect(bboxes[i], bboxes[j], pad):
                adj[i].append(j)
                adj[j].append(i)

    seen = [False] * n
    components = []
    for i in range(n):
        if seen[i]:
            continue
        stack = [i]
        seen[i] = True
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        components.append(comp)
    return components


def _filter_and_sort_components(
    components: List[List[int]],
    bboxes: List[Tuple[float, float, float, float]],
) -> List[List[int]]:
    """Drop tiny components and sort poses in row-major order."""
    valid = []
    for comp in components:
        if len(comp) < MIN_GROUPS_IN_POSE:
            continue
        x0, y0, x1, y1 = _union_bbox([bboxes[i] for i in comp])
        if (x1 - x0) < MIN_POSE_W or (y1 - y0) < MIN_POSE_H:
            continue
        valid.append(comp)

    def _row_major_key(c: List[int]) -> tuple:
        x0, y0, x1, y1 = _union_bbox([bboxes[i] for i in c])
        return (round(y0 // 100), x0)

    return sorted(valid, key=_row_major_key)


def _export_pose_svgs(
    root: ET.Element,
    groups: List[Tuple[int, ET.Element]],
    components: List[List[int]],
    bboxes: List[Tuple[float, float, float, float]],
    out_dir: Path,
    prefix: str = "pose",
) -> List[Path]:
    """Export each component as a standalone SVG with tight viewBox."""
    out_dir.mkdir(parents=True, exist_ok=True)
    base_w, base_h = _get_canvas_size(root)

    exported = []
    for k, comp in enumerate(components, start=1):
        x0, y0, x1, y1 = _union_bbox([bboxes[i] for i in comp])
        x0 = max(0.0, x0 - EXPORT_MARGIN)
        y0 = max(0.0, y0 - EXPORT_MARGIN)
        x1 = min(base_w, x1 + EXPORT_MARGIN)
        y1 = min(base_h, y1 + EXPORT_MARGIN)
        w, h = max(1.0, x1 - x0), max(1.0, y1 - y0)

        comp_sorted = sorted(comp, key=lambda i: groups[i][0])
        children = (groups[i][1] for i in comp_sorted)

        svg_str = _build_svg_wrapper(children, (x0, y0, w, h), root)
        out_path = out_dir / f"{prefix}_{k:02d}.svg"
        out_path.write_text(svg_str, encoding="utf-8")
        exported.append(out_path)

    return exported


def get_cropped_poses(
    input_file: str | Path = INPUT_FILE,
    output_dir: str | Path = OUTPUT_DIR,
    prefix: str = PREFIX,
) -> List[Path]:
    """
    Smart sprite cropping entry point.

    Args:
        input_file (str | Path, optional): The input SVG file to process. Defaults to INPUT_FILE.
        output_dir (str | Path, optional): The directory to save output SVG files. Defaults to OUTPUT_DIR.
        prefix (str, optional): The prefix for output file names. Defaults to PREFIX.

    Raises:
        FileNotFoundError: If the input file is not found.
        FileNotFoundError: If the input directory is not found.
        RuntimeError: If no drawable top-level <g> elements are detected.
        RuntimeError: If no valid poses are detected after clustering.

    Returns:
        List[Path]: A list of output SVG file paths.
    """
    input_file = Path(input_file)
    output_dir = Path(output_dir)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # check if input file is directory
    if input_file.is_dir():
        print(f"Input is a directory. Processing first SVG file found in it.")
        svg_files = list(input_file.glob("*.svg"))
        if not svg_files:
            raise FileNotFoundError(f"No SVG files found in directory: {input_file}")

        input_file = svg_files[0]


    root = _parse_svg(input_file)
    base_w, base_h = _get_canvas_size(root)
    top_groups = _collect_top_groups(root)

    bboxes = []
    valid_groups = []
    for idx, g in top_groups:
        bb = _raster_bbox_of_group(g, base_w, base_h, root, scale=RASTER_SCALE)
        if bb is not None:
            bboxes.append(bb)
            valid_groups.append((idx, g))

    if not valid_groups:
        raise RuntimeError("No drawable top-level <g> elements detected.")

    comps = _cluster_groups_into_poses(valid_groups, bboxes, pad=INTERSECT_PAD)
    comps = _filter_and_sort_components(comps, bboxes)

    if not comps:
        raise RuntimeError("No valid poses detected after clustering.")

    return _export_pose_svgs(root, valid_groups, comps, bboxes, output_dir, prefix)


def get_all_cropped_poses(
    input_dir: str | Path = SPRITES_SHEETS_DIR,
    output_dir: str | Path = OUTPUT_DIR,
    prefix: str = "pose",
) -> List[Path]:
    """
    Get all cropped poses from SVG files in the input directory.

    Args:
        input_dir (str | Path, optional): The directory containing input SVG files. Defaults to SPRITES_SHEETS_DIR.
        output_dir (str | Path, optional): The directory to save output SVG files. Defaults to OUTPUT_DIR.
        prefix (str, optional): The prefix for output file names. Defaults to PREFIX.

    Raises:
        FileNotFoundError: If the input directory is not found.

    Returns:
        list[Path]: A list of output directories created for each SVG file.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    output_dirs = []

    for svg_file in input_dir.glob("*.svg"):
        sprite_name = svg_file.stem

        curr_output_dir = output_dir / sprite_name
        curr_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\nProcessing '{svg_file.name}' into '{curr_output_dir}'")

        get_cropped_poses(svg_file, curr_output_dir, prefix)
        output_dirs.append(curr_output_dir)
        print("-" * 40)
    return output_dirs


if __name__ == "__main__":
    get_cropped_poses()
