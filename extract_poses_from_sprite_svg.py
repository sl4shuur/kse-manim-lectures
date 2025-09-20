from src.animations_sprites.crop_svg_sprite import get_all_cropped_poses, get_cropped_poses
from src.utils.config import SPRITES_SHEETS_DIR
from pathlib import Path

def get_poses_recursively() -> Path:
    """Get all poses from a specific sprite sheet file."""
    sprite_name = input("For example, 'player_vector': ").strip().removesuffix(".svg") + ".svg"
    input_path = SPRITES_SHEETS_DIR / sprite_name
    
    try:
        return get_cropped_poses(input_path)
    except FileNotFoundError:
        print(f"File {input_path.name} in folder {SPRITES_SHEETS_DIR} not found. Please try again.")
        return get_poses_recursively()  # Ask again
    except Exception as e:
        print(f"Error occurred while processing {input_path}: {e}")
        return get_poses_recursively()  # Ask again

if __name__ == "__main__":
    # Ask user for the type of cropping
    print("Make sure you have uploaded the SVG file(s) of sheet to the `assets/sprites_sheets` directory!!!")
    while True:
        choice = input("Do you want to crop all sprite sheets or a specific one? (all/specific): ").strip().lower()
        match choice:
            case "all" | "a":
                output_dirs = get_all_cropped_poses()
                print(f"\nAll done! Created cropped poses in: {output_dirs}")
                break
            case "specific" | "s":
                print("Enter the name of the sprites sheet (without .svg extension)")
                out = get_poses_recursively()
                print(f"\nAll done! Created cropped poses in: {out}")
                break
            case _:
                print("Invalid choice. Please enter 'all' or 'specific'.")