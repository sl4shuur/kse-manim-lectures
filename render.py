import os
import sys
import inspect
import argparse
from pathlib import Path
from manim import Scene

from src.utils.config import SOURCES_DIR


def _get_all_scenes():
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


def _find_scene_by_name(scene_name):
    """Find scene class by name"""
    all_scenes = _get_all_scenes()
    for module_name, class_name in all_scenes:
        if class_name == scene_name:
            return module_name, class_name
    return None, None


def render_scene(scene_name=None):
    """Render specified scene or default scene"""

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

    file_name = module_name.replace(".", "/") + ".py"
    print(f"Rendering scene: {class_name}")

    project_dir = Path(__file__).resolve().parent
    command = (
        f'docker run -it --rm -v "{project_dir}:/manim" -w /manim '
        f"-e PYTHONPATH=/manim "
        f"manimcommunity/manim manim {file_name} {class_name} -ql"
    )
    print(f"Running command: {command}")

    os.system(command)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Manim scenes")
    parser.add_argument("scene", nargs="?", help="Scene class name to render")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available scenes"
    )

    args = parser.parse_args()

    if args.list:
        all_scenes = _get_all_scenes()
        print("Available custom scenes:")
        for module_name, class_name in all_scenes:
            print(f"  {class_name} (from {module_name})")
    elif args.scene:
        render_scene(args.scene)
    else:
        # Show available scenes if no arguments
        all_scenes = _get_all_scenes()
        print("Available custom scenes:")
        for module_name, class_name in all_scenes:
            print(f"  {class_name}")
        print("\nUsage:")
        print("  python render.py <scene_name>    # Render specific scene")
        print("  python render.py --list          # List all scenes")
        print("  python render.py                 # Show this help")
