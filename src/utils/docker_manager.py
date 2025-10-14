import os
import subprocess
import time


def _is_docker_running() -> bool:
    """Check if Docker daemon is running"""
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _start_docker() -> bool:
    """Try to start Docker daemon"""
    print("Docker is not running. Attempting to start Docker...")

    try:
        # Try to start Docker Desktop on Windows
        if os.name == "nt":  # Windows
            print("Starting Docker Desktop on Windows...")
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Start-Process",
                    "'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'",
                ],
                check=False,
            )
        else:
            # For Linux/Mac, try starting docker service
            print("Starting Docker service...")
            subprocess.run(["sudo", "systemctl", "start", "docker"], check=False)

        # Wait for Docker to start and check multiple times
        print("Waiting for Docker to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if _is_docker_running():
                print(f"Docker started successfully after {i+1} seconds!\n")
                return True
            if (i + 1) % 5 == 0:
                print(f"Still waiting for Docker... ({i+1}/30 seconds)")

        print("Docker failed to start within 30 seconds.")
        return False

    except Exception as e:
        print(f"Error starting Docker: {e}")
        return False


def ensure_docker_running() -> bool:
    """Ensure Docker is running, start it if necessary"""
    print("Checking Docker status...")

    if _is_docker_running():
        print("Docker is already running!\n")
        return True

    print("Docker is not running.")
    return _start_docker()
