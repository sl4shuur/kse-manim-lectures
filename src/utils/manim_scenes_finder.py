import os
import sys
import inspect
from pathlib import Path
from manim import Scene

from src.utils.config import SOURCES_DIR

# List of built-in Manim scene classes to exclude
BUILTIN_SCENES = {
    "LinearTransformationScene",
    "MovingCameraScene",
    "SpecialThreeDScene",
    "ThreeDScene",
    "VectorScene",
    "ZoomedScene",
    "Scene",
}


def get_all_scenes() -> list[tuple[str, str]]:
    """
    Get only custom scene classes, excluding built-in Manim classes

    Returns:
        list[tuple[str, str]]: List of tuples containing (module_path#line_number, class_name)
    """
    scenes = []

    # Add SOURCES_DIR to sys.path
    sys.path.append(str(SOURCES_DIR))

    for root, _, files in os.walk(SOURCES_DIR):
        for file in files:
            if file.endswith(".py"):
                module_path = Path(root) / file
                # Convert the path to a module name (e.g., src.animations_lectures.24_1)
                relative_module = module_path.relative_to(SOURCES_DIR).with_suffix("")
                module_name = ".".join(relative_module.parts)
                try:
                    module = __import__(module_name, fromlist=["*"])
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # Check if it's a Scene subclass but not a built-in one
                        if (
                            issubclass(obj, Scene)
                            and obj is not Scene
                            and name not in BUILTIN_SCENES
                            and obj.__module__ == module_name
                        ):  # Only classes defined in this module
                            # Get line number where the class is defined
                            _, line_number = inspect.getsourcelines(obj)
                            scenes.append((f"{str(module_path.resolve())}#{line_number}", name))
                except Exception as e:
                    print(f"Error importing {module_path}: {e}")
    return scenes


def find_scene_by_name(scene_name: str) -> tuple[str, str] | tuple[None, None]:
    """Find scene class by name"""
    all_scenes = get_all_scenes()
    for module_path, class_name in all_scenes:
        if class_name == scene_name:
            return module_path, class_name
    return None, None
