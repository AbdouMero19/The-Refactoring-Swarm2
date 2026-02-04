import subprocess

def run_black(file_path):
    """Runs black formatter to fix style issues automatically."""
    try:
        subprocess.run(["black", file_path], check=True, capture_output=True)
    except Exception:
        pass # If black fails, just proceed