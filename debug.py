from src.animations_sprites.crop_svg_sprite import get_all_cropped_poses


if __name__ == "__main__":
    output_dirs = get_all_cropped_poses()
    print(f"\nAll done! Created cropped poses in: {output_dirs}")
