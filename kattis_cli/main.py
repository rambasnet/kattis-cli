""" Main module for the kattis_cli package."""
__version__ = '0.1.0'

from rich.console import Console
import click

import kattis_cli.download as download
import kattis_cli.ui as ui
import kattis_cli.program as program


@click.group()
def main():
    """
    CLI for downloading, testing and submitting Kattis problems.
    """


@main.command(help='Download sample data & metadata.')
@click.argument('problemid')
def get(problemid: str) -> None:
    """Command Line Interface for Kattis.
    """
    console = Console()
    console.print(
        f"Downloading samples: [bold blue]{problemid}[/bold blue]")
    download.download_sample_data(problemid)
    console.print(
        f"Downloading metadata: [bold blue]{problemid}[/bold blue]")
    download.load_problem_metadata(problemid)


@main.command(help='Show problem metadata.')
@click.option('-p', '--problemid', default='', help='Problem ID.')
def info(problemid: str) -> None:
    """Display problem metada.
    """
    ui.show_problem_meta_data(problemid)


@main.command(help='Test solution with sample files.')
@click.option('-p', '--problemid', default='', help='Problem ID')
@click.option('-l', '--language', default='', help='Language')
def test(problemid: str, language: str) -> None:
    """Test solution with sample files.
    """
    program.test_solution(problemid, language)


if __name__ == '__main__':
    main()
