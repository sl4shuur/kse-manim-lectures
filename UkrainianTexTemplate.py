from manim import TexTemplate, Scene, Tex, Write

UkrainianTexTemplate = TexTemplate(
    tex_compiler="xelatex",
    description="Ukrainian TeX Template",
    preamble=r"""
    \usepackage{fontspec}
    \usepackage{babel}
    \babelprovide[import, main]{ukrainian}
    \setmainfont{DejaVu Serif}
    \usepackage{amsmath, amssymb}
    """,
    output_format=".xdv",
)


class HelloDocker(Scene):
    def construct(self):
        formula = Tex(r"$Docker_{\text{привіт}}$", tex_template=UkrainianTexTemplate)
        self.play(Write(formula), run_time=3)
        self.wait()


if __name__ == "__main__":
    import os
    from pathlib import Path

    scene_to_render = HelloDocker.__name__
    print(f"Rendering scene: {scene_to_render}")

    project_dir = Path(__file__).resolve().parent
    file_name = Path(__file__).name
    command = f'docker run -it --rm -v "{project_dir}:/manim" -w /manim manimcommunity/manim manim {file_name} {scene_to_render} -ql'
    print(f"Running command: {command}")

    os.system(command)
