from manim import * # type: ignore


class Sprite(Scene):
    def construct(self):
        sprite = SVGMobject("assets/sprites_poses/adventurer_vector/pose_01.svg")
        self.play(DrawBorderThenFill(sprite))
        self.wait(1)

