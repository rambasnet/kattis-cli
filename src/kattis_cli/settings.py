"""Settings for the project."""

from pathlib import Path
from rich.console import Console

KATTIS_PROBLEM_URL = "https://open.kattis.com/problems/"
KATTIS_SOURCE_URL = "https://open.kattis.com/problem-sources/"


def check_kattisrc() -> None:
    """Check if kattisrc file exists."""
    console = Console()
    kattisrc = Path.home() / ".kattisrc"
    if not kattisrc.is_file():
        console.print("kattisrc file not found.", style='red bold')
        console.print("Download kattisrc file: \
                         https://open.kattis.com/info/submit.", 'red, bold')
        exit(1)
