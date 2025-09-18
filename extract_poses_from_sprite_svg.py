from src.animations_sprites.crop_svg_sprite import get_all_cropped_poses, get_cropped_poses

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
                sprite_name = input("For example, 'player_vector': ").strip().removesuffix(".svg") + ".svg"
                get_cropped_poses(sprite_name)
            case _:
                print("Invalid choice. Please enter 'all' or 'specific'.")