from manim import *  # type: ignore
from src.animations_sprites.ManimSprite import ManimSprite
from src.utils.config import POSES_NUM_LIST

### Poses (groups) with good transitions for almost all sprites:
# 01 - 14 - 08 - 19
# 12 - 15
# 16 - 24


class PoseSwitcher(Scene):
    def construct(self):
        sprite = ManimSprite("player")

        # animate the appearance
        self.play(DrawBorderThenFill(sprite.cur_manim_svgmobject))
        self.wait()
        self.clear()

        # for loop to check all poses changing animations
        for i in range(len(POSES_NUM_LIST)):
            for j in range(len(POSES_NUM_LIST)):
                if i < j:
                    sprite.change_pose(POSES_NUM_LIST[i])
                    sprite.change_pose(POSES_NUM_LIST[j])
                    init_pose = sprite.old_manim_svgmobject
                    cur_pose = sprite.cur_manim_svgmobject
                    text = Text(
                        f"Pose {POSES_NUM_LIST[i]} to {POSES_NUM_LIST[j]}"
                    ).to_edge(UP)

                    self.add(init_pose, text)
                    self.play(Transform(init_pose, cur_pose), run_time=1)
                    self.wait()
                    self.clear()

        # animate the disappearance (for 14 poses it looks better)
        sprite.change_pose("14")
        self.play(DrawBorderThenFill(sprite.cur_manim_svgmobject), reverse=True)
        self.wait()

class AllSpritesAnimation(Scene):
    def construct(self):
        sprite_names = [
            "adventurer",
            # "female", # works bad with current poses
            "player",
            "soldier",
            "zombie"
        ]
        poses = ["01", "08", "14", "19"]

        for sprite_name in sprite_names:
            sprite = ManimSprite(sprite_name, scale=3)
            for i in range(len(poses)):
                for j in range(len(poses)):
                    if i < j:
                        sprite.change_pose(poses[i])
                        sprite.change_pose(poses[j])
                        init_pose = sprite.old_manim_svgmobject
                        cur_pose = sprite.cur_manim_svgmobject
                        text = Text(
                            f"{sprite_name} Pose {poses[i]} to {poses[j]}", font_size=12
                        ).to_edge(UP)

                        self.add(init_pose, text)
                        self.play(Transform(init_pose, cur_pose))
                        self.wait(0.5)
                        self.clear()