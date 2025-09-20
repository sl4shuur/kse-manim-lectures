from pathlib import Path
from src.utils.config import POSES_NUM_LIST, SPRITES_POSES_DIR, POSE_PREFIX
from manim import SVGMobject


class ManimSprite:
    def __init__(
        self,
        sprite_name: str = "player",
        sprites_poses_dir: str | Path = SPRITES_POSES_DIR,
        poses_dir: str | Path | None = None,
        pose_prefix: str = POSE_PREFIX,
        scale: float = 2.0,
        position: tuple[float, float, float] = (0, 0, 0),
    ):
        self.sprite_name = sprite_name.lower()
        self.sprites_poses_dir = Path(sprites_poses_dir)
        self.poses_dir = Path(poses_dir) if poses_dir else self._get_poses_dir()
        self.scale = scale
        self.position = position
        self.poses_dir = self._get_poses_dir()
        self.pose_prefix = pose_prefix
        self.poses_num_list = POSES_NUM_LIST
        self.cur_manim_svgmobject = self._get_manim_svgmobject(self.poses_num_list[0])
        self.old_manim_svgmobject = self._get_manim_svgmobject(self.poses_num_list[-1])

    def _get_poses_dir(self):
        cur_poses_dir = self.sprites_poses_dir / self.sprite_name
        if not cur_poses_dir.exists() or not cur_poses_dir.is_dir():
            new_poses_dir = self.sprites_poses_dir / (self.sprite_name + "_vector")
            if new_poses_dir.exists() and new_poses_dir.is_dir():
                cur_poses_dir = new_poses_dir
            else:
                raise FileNotFoundError(f"Directory for sprite '{self.sprite_name}' not found in {self.sprites_poses_dir}")
        return cur_poses_dir
    
    def _get_manim_svgmobject(self, pose_num: str) -> SVGMobject:

        pose_file = self.poses_dir / f"{self.pose_prefix}{pose_num}.svg"
        if not pose_file.exists() or not pose_file.is_file():
            raise FileNotFoundError(f"Pose file '{pose_file}' not found.")
        svg_mobject = SVGMobject(str(pose_file))
        svg_mobject.scale(self.scale)
        svg_mobject.move_to(self.position)
        return svg_mobject
    
    def change_pose(self, new_pose_num: str):
        if new_pose_num not in self.poses_num_list:
            raise ValueError(f"Pose number '{new_pose_num}' is not in the list of available poses: {self.poses_num_list}")
        self.old_manim_svgmobject = self.cur_manim_svgmobject
        self.cur_manim_svgmobject = self._get_manim_svgmobject(new_pose_num)
