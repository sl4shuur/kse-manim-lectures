from src.animations_sprites.manim_sprtites import Sprite

if __name__ == "__main__":
    import os
    from pathlib import Path

    scene_to_render = Sprite.__name__
    file_name = Sprite.__module__.replace(".", "/") + ".py"
    print(f"Rendering scene: {scene_to_render}")

    project_dir = Path(__file__).resolve().parent
    command = f'docker run -it --rm -v "{project_dir}:/manim" -w /manim manimcommunity/manim manim {file_name} {scene_to_render} -ql'
    print(f"Running command: {command}")

    os.system(command)