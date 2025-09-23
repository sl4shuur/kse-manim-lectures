import os
import argparse
from pathlib import Path

from src.utils.env_manager import ensure_venv_active
from src.utils.config import SOURCES_DIR
from src.utils.docker_manager import ensure_docker_running

# Ensure virtual environment is active
if not ensure_venv_active():
    print("❌ Cannot proceed without an active virtual environment.")
    print("Please check the README file to set up the environment.")
    print("Run the following commands manually:")
    print("  uv sync")
    print("  .venv\\Scripts\\activate  # Windows")
    print("  source .venv/bin/activate  # Linux/Mac")
    raise SystemExit(1)

from src.utils.manim_scenes_finder import get_all_scenes, find_scene_by_name


def _get_quality_folder(quality: str) -> str:
    """Map quality flag to output folder name"""
    quality_mapping = {
        "ql": "480p15",
        "qm": "720p30",
        "qh": "1080p60",
        "qp": "1440p60",
        "qk": "2160p60"
    }
    return quality_mapping.get(quality, "480p15")


def _build_expected_video_path(module_name: str, class_name: str, quality: str, project_dir: Path) -> Path:
    """Build expected local video path"""
    # Extract file name from module (e.g., "animations_lectures.24_1" -> "24_1")
    file_name = module_name.split(".")[-1]
    quality_folder = _get_quality_folder(quality)

    video_path = project_dir / "media" / "videos" / file_name / quality_folder / f"{class_name}.mp4"
    return video_path


def render_scene(scene_name: str, quality: str = "ql"):
    """Render specified scene or default scene"""

    # Ensure Docker is running
    if not ensure_docker_running():
        print("❌ Cannot proceed without Docker running.")
        print("Please start Docker manually and try again.")
        return

    if scene_name:
        module_name, class_name = find_scene_by_name(scene_name)
        if not class_name:
            print(f"Scene '{scene_name}' not found!")
            print("Available scenes:")
            all_scenes = get_all_scenes()
            for mod_name, cls_name in all_scenes:
                print(f"  {cls_name}")
            return
    else:
        # Default scene if no argument provided
        class_name = "Indications"
        module_name = "test_scenes.test_ukr_tex"

    if not module_name:
        print(f"Cannot determine module for scene '{class_name}'")
        return

    # Calculate relative path from project root to the source file
    project_dir = Path(__file__).resolve().parent
    source_file_path = SOURCES_DIR / module_name.replace(".", "/")
    source_file_path = source_file_path.with_suffix(".py")

    # Get relative path from project root
    file_name = source_file_path.relative_to(project_dir).as_posix()

    print(f"\n🎬 Rendering scene: {class_name} with quality: {quality}")

    command = (
        f'docker run -it --rm -v "{project_dir}:/manim" -w /manim '
        f"-e PYTHONPATH=/manim "
        f"manimcommunity/manim manim {file_name} {class_name} -{quality}"
    )
    print(f"🐳 Running command: {command}")

    try:
        exit_code = os.system(command)

        if exit_code == 0:
            print("\n✅ Rendering completed!")

            # Build expected video path and show location
            expected_path = _build_expected_video_path(module_name, class_name, quality, project_dir)
            if expected_path.exists():
                print(f"📹 Video file ready at: {expected_path}")
            else:
                print(f"📹 Expected video location: {expected_path}")
                print("⚠️  Video file not found at expected location.")
        else:
            print(f"\n❌ Rendering failed with exit code: {exit_code}")

    except Exception as e:
        print(f"❌ Error during rendering: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Manim scenes")
    parser.add_argument("scene", nargs="?", help="Scene class name to render")
    parser.add_argument(
        "-ql", "--quality-low", action="store_const", const="ql", dest="quality",
        help="Render in low quality (854x480p15FPS)"
    )
    parser.add_argument(
        "-qm", "--quality-medium", action="store_const", const="qm", dest="quality",
        help="Render in medium quality (1280x720p30FPS)"
    )
    parser.add_argument(
        "-qh", "--quality-high", action="store_const", const="qh", dest="quality",
        help="Render in high quality (1920x1080p60FPS)"
    )
    parser.add_argument(
        "-qp", "--quality-production", action="store_const", const="qp", dest="quality",
        help="Render in production 2K quality (2560x1440p60FPS)"
    )
    parser.add_argument(
        "-qk", "--quality-4k", action="store_const", const="qk", dest="quality",
        help="Render in 4K quality (3840x2160p60FPS)"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available scenes"
    )

    # Set default quality if none specified
    parser.set_defaults(quality="ql")

    args = parser.parse_args()

    if args.list:
        all_scenes = get_all_scenes()
        print("Available custom scenes:")
        for module_name, class_name in all_scenes:
            print(f"  {class_name} (from {module_name})")
    elif args.scene:
        render_scene(args.scene, args.quality)
    else:
        # Show available scenes if no arguments
        all_scenes = get_all_scenes()
        print("Available custom scenes:")
        for module_name, class_name in all_scenes:
            print(f"  {class_name}")
        print("\nUsage:")
        print("  python render.py <scene_name> [-ql|-qm|-qh|-qp|-qk]  # Render scene with quality (default: -ql, low)")
        print("  python render.py --list                              # List all scenes")
        print("  python render.py                                     # Show this help")
        print("\nQuality options:")
        print("  -ql, --quality-low         Low quality (854x480p15FPS)")
        print("  -qm, --quality-medium      Medium quality (1280x720p30FPS)")
        print("  -qh, --quality-high        High quality (1920x1080p60FPS)")
        print("  -qp, --quality-production  Production 2K quality (2560x1440p60FPS)")
        print("  -qk, --quality-4k          4K quality (3840x2160p60FPS)")
