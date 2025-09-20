from manim import *  # type: ignore
from src.animations_sprites.ManimSprite import ManimSprite
from src.utils.config import POSES_NUM_LIST

# ["04", "05", "06", "14", "15", "18", "19", "24"]
# 04 - 18
# 05 - 06 - 15 - 19


class PoseSwitcher(Scene):
    def construct(self):
        sprite = ManimSprite("adventurer")

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
                    self.clear()
                    self.wait(0.2)
