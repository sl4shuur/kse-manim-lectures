from manim import TexTemplate, Scene, NumberPlane

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

def turn_debug_mode_on(scene: Scene, opacity: float = 0.5) -> NumberPlane:
    """
    Enable debug mode by adding a grid to the scene with specified opacity.
    It helps in aligning and positioning elements during development.
    Directions like UP, DOWN, LEFT, RIGHT, ORIGIN can be used to position elements.

    Args:
        self (Scene): The scene to modify.
        opacity (float, optional): The opacity of the grid. Defaults to 0.5.

    Returns:
        NumberPlane: The grid added to the scene.
    """
    grid = NumberPlane()
    grid.set_opacity(opacity)
    scene.add(grid)
    return grid
    
