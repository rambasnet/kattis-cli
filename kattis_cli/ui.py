"""User interface for the Kattis CLI.

This module exposes a UIManager that renders problem metadata and a
module-level `show_problem_metadata` function delegating to a default
UIManager instance for backward compatibility.
"""

from typing import Any, Dict, Optional, Protocol
from rich.console import Console
from rich.table import Table
from rich import box
from rich.align import Align
from . import download
from . import settings


class UIManager:
    """Handles UI rendering tasks (currently: problem metadata)."""

    class DownloadManagerLike(Protocol):
        """Protocol describing the minimal download manager API used here."""

        def load_problem_metadata(self, problemid: str = '') -> Dict[Any, Any]:
            ...

    def __init__(
        self,
        download_manager: Optional["UIManager.DownloadManagerLike"] = None,
    ) -> None:
        # Accept a download manager for dependency injection; fall back to
        # the module-level functions in `download` for compatibility.
        # Use structural typing (Protocol) so both the manager instance and
        # the legacy module object satisfy the type checker.
        self.download_manager = download_manager or download

    def show_problem_metadata(self, problemid: str = '') -> Dict[Any, Any]:
        """Render and print metadata for a problem.

        If `problemid` is provided the metadata for that problem is shown.
        If omitted, the method attempts to find a problem folder in the
        current working directory and show its metadata.

        Returns the metadata dictionary as loaded from disk or an empty
        dict when no metadata is available.
        """

        console = Console()
        metadata = self.download_manager.load_problem_metadata(problemid)
        if metadata:
            table = Table(
                title=f"[not italic bold blue]{metadata['title']}[/]")
            table.box = box.SQUARE
            Align.center(table)
            table.add_column(
                "Problem ID",
                justify="center",
                style="cyan",
                no_wrap=False)
            table.add_column(
                "Difficulty",
                justify="center",
                style="cyan",
                no_wrap=False)
            table.add_column(
                "CPU Limit",
                justify="center",
                style="cyan",
                no_wrap=False)
            table.add_column(
                "Memory Limit",
                justify="center",
                style="cyan",
                no_wrap=False)
            table.add_column(
                "Submissions",
                justify="center",
                style="cyan",
                no_wrap=False)
            table.add_column(
                "Accepted",
                justify="center",
                style="cyan",
                no_wrap=False)

            p_id = metadata['problemid']
            problem_link = f"[link={settings.KATTIS_PROBLEM_URL}{p_id}]"
            problem_link += f"{p_id}[/link]"
            table.add_row(problem_link,
                          metadata['difficulty'],
                          metadata['cpu_limit'],
                          metadata['mem_limit'],
                          str(metadata['submissions']),
                          str(metadata['accepted'])
                          )

            console.print(table)
        elif problemid:
            error = "Problem metadata for problemid: [bold blue]"
            error += f"{problemid}[/bold blue] not found."
            console.print(error, style='red bold')
            suggest = "Download problem metadata using: [bold blue]"
            suggest += f"kattis get {problemid}[/bold blue]"
            console.print(suggest, style='red bold')
        else:
            error = "Kattis problem folder with meta data "
            error += "not found in current directory."
            console.print(error, style='red bold')
            suggest = "Download problem metadata using: [bold blue]"
            suggest += "kattis get <problemid>[/bold blue]"
            console.print(suggest, style='red bold')

        return metadata


# Default UI manager for module-level compatibility functions
_ui_manager = UIManager()


def show_problem_metadata(problemid: str = '') -> Dict[Any, Any]:
    """Module-level convenience wrapper for :class:`UIManager`.

    This keeps the original functional API working for scripts that
    expect a `show_problem_metadata` function.
    """

    return _ui_manager.show_problem_metadata(problemid)
