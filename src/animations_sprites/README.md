# Animated Sprites with Manim

This directory contains a Manim scene that demonstrates how to work with animated sprites using SVG files.

## Files

The source files are located in the `assets/sprites_sheets` directory. These files include various poses of a character in SVG format.
These files were sourced from [Kenney.nl](https://kenney.nl/assets/platformer-characters). All credits go to the original creator.

You can find other sprite assets on Internet resources or create your own using vector graphic software like Adobe Illustrator or Inkscape.

## How to crop into poses

> [!IMPORTANT]
> Before using the sprites, ensure that you have uploaded the SVG file(s) of sheet to the `assets/sprites_sheets` directory.

To extract individual poses from a sprite sheet SVG file, you can use the `extract_poses_from_sprite_svg.py` script located in the root directory. This script will help you crop the sprite sheet into separate SVG files for each pose.

Run the script with the following command:

```bash
uv run extract_poses_from_sprite_svg.py
```

and follow the prompts to specify the input SVG file and/or the desired sheets directory.

## Usage

To use these sprites in your Manim scenes, you can import the `ManimSprite` class from the `src.animations_sprites.ManimSprite` module and create instances of it in your scenes. For example:

```python
from manim import *  # type: ignore
from src.animations_sprites.ManimSprite import ManimSprite

class MyScene(Scene):
    def construct(self):
        sprite = ManimSprite("adventurer", scale=3)
        self.play(DrawBorderThenFill(sprite.cur_manim_svgmobject))
        self.wait(1)

        sprite.set_pose("08")
        self.play(Transform(sprite.old_manim_svgmobject, sprite.cur_manim_svgmobject))
        self.wait(1)
```

See more examples in the `manim_sprites.py` file.
