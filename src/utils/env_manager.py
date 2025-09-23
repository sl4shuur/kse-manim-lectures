import os
import sys
import subprocess
from pathlib import Path

from src.utils.config import BASE_DIR, VENV_NAMES


def _is_venv_active() -> bool:
    """Check if virtual environment is currently active"""
    # Check if we're in a virtual environment
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def _find_venv_path() -> Path | None:
    """Find virtual environment in project directory"""

    for venv_name in VENV_NAMES:
        venv_path = BASE_DIR / venv_name
        if venv_path.exists():
            # Check if it's actually a virtual environment
            if os.name == "nt":  # Windows
                activate_script = venv_path / "Scripts" / "activate.bat"
                python_exe = venv_path / "Scripts" / "python.exe"
            else:  # Linux/Mac
                activate_script = venv_path / "bin" / "activate"
                python_exe = venv_path / "bin" / "python"

            if activate_script.exists() and python_exe.exists():
                return venv_path

    return None


def _activate_venv(venv_path: Path) -> bool:
    """Activate virtual environment for current process"""
    try:
        if os.name == "nt":  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            python_exe = venv_path / "Scripts" / "python.exe"
            scripts_dir = venv_path / "Scripts"
        else:  # Linux/Mac
            activate_script = venv_path / "bin" / "activate"
            python_exe = venv_path / "bin" / "python"
            scripts_dir = venv_path / "bin"

        # Update environment variables
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        os.environ["PATH"] = f"{scripts_dir}{os.pathsep}{os.environ['PATH']}"

        # Update sys.prefix to simulate activation
        sys.prefix = str(venv_path)
        sys.exec_prefix = str(venv_path)

        # Update sys.path to use venv packages
        site_packages = (
            venv_path / "Lib" / "site-packages"
            if os.name == "nt"
            else venv_path / "lib" / "python3.11" / "site-packages"
        )
        if site_packages.exists() and str(site_packages) not in sys.path:
            sys.path.insert(0, str(site_packages))

        print(f"Virtual environment activated: {venv_path}\n")
        return True

    except Exception as e:
        print(f"Error activating virtual environment: {e}")
        return False


def _install_requirements(venv_path: Path) -> bool:
    """Install requirements if requirements.txt exists"""

    requirements_file = BASE_DIR / "requirements.txt"

    if not requirements_file.exists():
        print("No requirements.txt found, skipping package installation.")
        return True

    try:
        if os.name == "nt":  # Windows
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:  # Linux/Mac
            pip_exe = venv_path / "bin" / "pip"

        print("Installing requirements...")
        subprocess.run(
            [str(pip_exe), "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True,
        )

        print("Requirements installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return False
    except Exception as e:
        print(f"Error installing requirements: {e}")
        return False


def ensure_venv_active() -> bool:
    """Ensure virtual environment is active"""
    print("Checking virtual environment status...")

    # Check if already in virtual environment
    if _is_venv_active():
        print("Virtual environment is already active!")
        return True

    print("Virtual environment is not active.")

    # Try to find existing virtual environment
    venv_path = _find_venv_path()

    if venv_path:
        print(f"Found virtual environment at: {venv_path}")
        return _activate_venv(venv_path)
    else:
        print("No virtual environment found.")
        return False
