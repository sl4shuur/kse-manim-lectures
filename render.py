import os
import sys
import inspect
import argparse
import subprocess
import time
from pathlib import Path
from manim import Scene

from src.utils.config import SOURCES_DIR


def _get_all_scenes() -> list[tuple[str, str]]:
    """Get only custom scene classes, excluding built-in Manim classes"""
    scenes = []

    # List of built-in Manim scene classes to exclude
    builtin_scenes = {
        "LinearTransformationScene",
        "MovingCameraScene",
        "SpecialThreeDScene",
        "ThreeDScene",
        "VectorScene",
        "ZoomedScene",
        "Scene",
    }

    sys.path.append(str(SOURCES_DIR))
    for root, _, files in os.walk(SOURCES_DIR):
        for file in files:
            if file.endswith(".py"):
                module_path = Path(root) / file
                relative_module = module_path.relative_to(SOURCES_DIR).with_suffix("")
                module_name = ".".join(relative_module.parts)
                try:
                    module = __import__(module_name, fromlist=["*"])
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Check if it's a Scene subclass but not a built-in one
                        if (
                            issubclass(obj, Scene)
                            and obj is not Scene
                            and name not in builtin_scenes
                            and obj.__module__ == module_name
                        ):  # Only classes defined in this module
                            scenes.append((module_name, name))
                except Exception as e:
                    print(f"Error importing {module_name}: {e}")
    return scenes


def _find_scene_by_name(scene_name: str) -> tuple[str, str] | tuple[None, None]:
    """Find scene class by name"""
    all_scenes = _get_all_scenes()
    for module_name, class_name in all_scenes:
        if class_name == scene_name:
            return module_name, class_name
    return None, None


def _is_docker_running() -> bool:
    """Check if Docker daemon is running"""
    try:
        result = subprocess.run(
            ["docker", "info"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _start_docker() -> bool:
    """Try to start Docker daemon"""
    print("Docker is not running. Attempting to start Docker...")

    try:
        # Try to start Docker Desktop on Windows
        if os.name == "nt":  # Windows
            print("Starting Docker Desktop on Windows...")
            subprocess.run([
                "powershell", "-Command", 
                "Start-Process", "'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'"
            ], check=False)
        else:
            # For Linux/Mac, try starting docker service
            print("Starting Docker service...")
            subprocess.run(["sudo", "systemctl", "start", "docker"], check=False)

        # Wait for Docker to start and check multiple times
        print("Waiting for Docker to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if _is_docker_running():
                print(f"Docker started successfully after {i+1} seconds!")
                return True
            if (i + 1) % 5 == 0:
                print(f"Still waiting for Docker... ({i+1}/30 seconds)")

        print("Docker failed to start within 30 seconds.")
        return False

    except Exception as e:
        print(f"Error starting Docker: {e}")
        return False


def _ensure_docker_running() -> bool:
    """Ensure Docker is running, start it if necessary"""
    print("Checking Docker status...")

    if _is_docker_running():
        print("Docker is already running!")
        return True

    print("Docker is not running.")
    return _start_docker()


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
    if not _ensure_docker_running():
        print("❌ Cannot proceed without Docker running.")
        print("Please start Docker manually and try again.")
        return

    if scene_name:
        module_name, class_name = _find_scene_by_name(scene_name)
        if not class_name:
            print(f"Scene '{scene_name}' not found!")
            print("Available scenes:")
            all_scenes = _get_all_scenes()
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
        all_scenes = _get_all_scenes()
        print("Available custom scenes:")
        for module_name, class_name in all_scenes:
            print(f"  {class_name} (from {module_name})")
    elif args.scene:
        render_scene(args.scene, args.quality)
    else:
        # Show available scenes if no arguments
        all_scenes = _get_all_scenes()
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
