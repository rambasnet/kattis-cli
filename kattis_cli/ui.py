"""User interface for the Kattis CLI.
"""

from typing import Any, Dict
from rich.console import Console
from rich.table import Table
from rich import box
from rich.align import Align
from . import download
from . import settings


def show_problem_metadata(problemid: str = '') -> Dict[Any, Any]:
    """Show problem metadata.

    Args:
        problemid (str): problemid
    """
    console = Console()
    metadata = download.load_problem_metadata(problemid)
    # print('metadata', metadata)
    if metadata:
        table = Table(title=f"[not italic bold blue]{metadata['title']}[/]")
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
        table.add_column(
            "Source",
            justify="center",
            style="cyan",
            no_wrap=False)
        # [link=https://www.willmcgugan.com]blog[/link]
        p_id = metadata['problemid']
        problem_link = f"[link={settings.KATTIS_PROBLEM_URL}{p_id}]"
        problem_link += f"{p_id}[/link]"
        source = metadata['source']
        sources_link = f"[link={settings.KATTIS_SOURCE_URL}{source}]"
        sources_link += f"{source}[/link]"
        # console.print(sources_link)
        table.add_row(problem_link,
                      metadata['difficulty'],
                      metadata['cpu_limit'],
                      metadata['mem_limit'],
                      str(metadata['submissions']),
                      str(metadata['accepted']),
                      sources_link)

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
