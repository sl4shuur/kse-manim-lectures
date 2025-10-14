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


def _build_expected_video_path(module_name: str, class_name: str, quality: str) -> tuple[Path, Path]:
    """Build expected local video path"""
    # Extract file name from module (e.g., "animations_lectures.24_1" -> "24_1")
    file_name = module_name.split(".")[-1]
    quality_folder = _get_quality_folder(quality)
    media_dir = Path("media")
    video_path = media_dir / "videos" / file_name / quality_folder / f"{class_name}.mp4"
    image_path = media_dir / "images" / file_name / f"{class_name}_ManimCE_v0.19.0.png"
    return video_path, image_path


def render_scenes(scene_names: list[str], quality: str = "ql"):
    """Render specified scenes or default scene"""
    # Ensure Docker is running
    if not ensure_docker_running():
        print("❌ Cannot proceed without Docker running.")
        print("Please start Docker manually and try again.")
        return
    
    print(f"Rendering scenes: {scene_names} with quality: {quality}")

    successful_scenes = []
    for scene_name in scene_names:
        module_name, class_name = find_scene_by_name(scene_name)
        if not class_name:
            print(f"Scene '{scene_name}' not found!")
            print("Available scenes:")
            all_scenes = get_all_scenes()
            for _, cls_name in all_scenes:
                print(f"  {cls_name}")
            continue

        if not module_name:
            print(f"Cannot determine module for scene '{class_name}'")
            continue

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
                successful_scenes.append(class_name)

                # Build expected video path and show location
                expected_path, image_path = _build_expected_video_path(module_name, class_name, quality)
                if expected_path.exists():
                    print(f"📹 Video file ready at: {expected_path}")
                else:
                    print("⚠️  Video file not found at expected location.")

                if image_path.exists():
                    print(f"🖼️ Image file ready at: {image_path}")
                else:
                    print("⚠️  Image file not found at expected location.")
            else:
                print(f"\n❌ Rendering failed with exit code: {exit_code}")

        except Exception as e:
            print(f"❌ Error during rendering: {e}")

    print("\n🎉 Successfully rendered scenes:")
    for scene in successful_scenes:
        print(f"  - {scene}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Manim scenes")
    parser.add_argument("scenes", nargs="?", help="Comma-separated list of scene class names to render")
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
    elif args.scenes:
        # Split scenes by comma and render each
        scene_list = [scene.strip() for scene in args.scenes.split(",")]
        render_scenes(scene_list, args.quality)
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
