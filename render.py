from src.animations_sprites.manim_sprites import PoseSwitcher, AllSpritesAnimation
from src.test_scenes.test_ukr_tex import UkrainianTexTest, Indications

if __name__ == "__main__":
    import os
    from pathlib import Path

    class_to_render = Indications

    scene_to_render = class_to_render.__name__
    file_name = class_to_render.__module__.replace(".", "/") + ".py"
    print(f"Rendering scene: {scene_to_render}")

    project_dir = Path(__file__).resolve().parent
    command = (
        f'docker run -it --rm -v "{project_dir}:/manim" -w /manim '
        f"-e PYTHONPATH=/manim "
        f"manimcommunity/manim manim {file_name} {scene_to_render} -ql"
    )
    print(f"Running command: {command}")

    os.system(command)
