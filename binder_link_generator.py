from src.utils.config import NOTEBOOKS_DIR
from pathlib import Path

GH_REPO = "sl4shuur/kse-manim-lectures"


def find_repo_root(start: Path) -> Path:
    """Find repository root by looking for a .git directory upwards."""
    p = start.resolve()
    for candidate in (p, *p.parents):
        if (candidate / ".git").exists():
            return candidate
    # fallback: try to locate by repo name folder inside parents
    repo_name = GH_REPO.split("/", 1)[-1]
    for candidate in (p, *p.parents):
        if candidate.name == repo_name:
            return candidate.parent
    # last resort: return NOTEBOOKS_DIR parent
    return NOTEBOOKS_DIR.resolve().parent


def get_all_notebooks(dir=NOTEBOOKS_DIR) -> list[Path]:
    """Get a list of all Jupyter notebooks in the notebooks directory."""
    notebooks = list(dir.glob("*.ipynb"))
    if not notebooks:
        print(f"No notebooks found in {dir}. Please add some notebooks or check the directory path.")
        raise FileNotFoundError(f"No notebooks found in {dir}")
    return notebooks


def generate_binder_link(
    git_branch="main", notebook_path="notebooks/manim_sprites.ipynb"
):
    """Generate a Binder link for the given Git branch."""
    # fix slash in branch name for URL
    git_branch = git_branch.replace("/", "%2F")

    print(f"\nGenerating Binder link for branch: {git_branch} (allowed slashes are replaced with %2F)")
    print("If you get some error, please check the branch name and try again.")

    return f"https://mybinder.org/v2/gh/{GH_REPO}/{git_branch}?urlpath=lab/tree/{notebook_path}"


def select_notebook_recursively(notebooks: list[Path]) -> Path:
    try:
        index = int(input("\nSelect a notebook by index: "))
        return notebooks[index]
    except IndexError:
        print("Invalid index. Please choose a valid index from the list.")
        return select_notebook_recursively(notebooks)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e


def user_ui(git_branch: str, notebooks_directory: Path):
    print(f"Looking for notebooks in: {notebooks_directory}")
    notebooks = get_all_notebooks(notebooks_directory)

    print("Available notebooks:")
    for i, nb in enumerate(notebooks):
        print(f"[{i}] {nb.name}")

    selected_nb = select_notebook_recursively(notebooks)
    print(f"Selected notebook: {selected_nb.name}")

    repo_root = find_repo_root(notebooks_directory)
    nb_dir_from_root = notebooks_directory.relative_to(repo_root)

    final_path = str(nb_dir_from_root) + "/" + selected_nb.name

    binder_link = generate_binder_link(git_branch=git_branch, notebook_path=final_path)
    print(f"\nBinder link:\n{binder_link}")


if __name__ == "__main__":
    user_ui("main", NOTEBOOKS_DIR)
