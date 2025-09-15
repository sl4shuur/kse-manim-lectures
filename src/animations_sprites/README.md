# Animated Sprites with Manim

This directory contains a Manim scene that demonstrates how to work with animated sprites using SVG files.

## Files

The source files are located in the `assets/sprites_sheets` directory. These files include various poses of a character in SVG format.
These files were sourced from [Kenney.nl](https://kenney.nl/assets/platformer-characters). All credits go to the original creator.

You can find other sprite assets on Internet resources or create your own using vector graphic software like Adobe Illustrator or Inkscape.

## Usage

To use these sprites in your Manim scenes, you can import the `Sprite` class from the `manim_sprites` module and create instances of it in your scenes. For example:

```python
from manim import *
from src.animations_sprites.manim_sprites import Sprite

class MyScene(Scene):
    def construct(self):
        sprite = Sprite()
        self.add(sprite)
        self.play(DrawBorderThenFill(sprite))
        self.wait(1)
```
