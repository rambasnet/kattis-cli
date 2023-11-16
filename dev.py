""" Main module for the kattis_cli package."""
__version__ = '0.1.0'

from pathlib import Path
import sys
import os
from typing import Tuple
from rich.console import Console
import click
import kattis_cli.download as download
import kattis_cli.ui as ui
import kattis_cli.program as program
import kattis_cli.kattis as kattis
import kattis_cli.utils.utility as utility


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
@click.option('-l', '--language', default='python', help='Language')
@click.option('-f', '--mainfile', default='', help='Main file')
def test(problemid: str, language: str, mainfile: str) -> None:
    """Test solution with sample files.
    """
    program.test_solution(problemid, language=language, main_file=mainfile)


@main.command(help='Submit a solution to Kattis.')
@click.option('-p', '--problemid', default='',
              help='Which problem to submit to.')
@click.option('-l', '--language', default='', help='Sets language')
@click.option('-m', '--mainclass', default='', help='Sets mainclass.')
@click.option("-t", '--tag', help="Disable all prompts",
              flag_value=True, default=False)
@click.option('-f',
              '--force',
              help="Force, no confirmation prompt before submission",
              flag_value=True,
              default=False)
@click.option('--folder', default='.', help='Problem folder')
@click.argument('files', nargs=-1, required=False)
def submit(problemid: str, language: str,
           mainclass: str, tag: str, force: bool,
           folder: str, files: Tuple[str]) -> None:
    """Submit a solution to Kattis.
    """
    folder = str(Path.cwd().joinpath(folder)) if folder else str(Path.cwd())
    console = Console()
    # check if files are given
    _files = list(files) if files else []
    if not _files:
        _files = [
            f for f in os.listdir(folder) if utility.valid_extension(f)]
        print(_files)
    if not _files:
        console.print(
            'No source file(s) found in the current folder!',
            style='bold red')
        exit(1)
    # check if problemid is given
    if not problemid:
        print(f'{folder=}')
        for f in _files:
            try:
                root_folder = utility.find_problem_root_folder(
                    folder, f.lower())
                problemid = root_folder.name
                break
            except FileNotFoundError:
                # print(ex)
                pass
    if not problemid:
        console.print('No problemid specified and I failed to guess \
problemid from filename(s) and current workding dir path.', style='bold red')
        sys.exit(1)
    # check if language
    if not language:
        _, ext = os.path.splitext(os.path.basename(_files[0]))
        # Guess language from files
        language = utility.guess_language(ext, _files)
        if not language:
            console.print(f'''\
No language specified, and I failed to guess language from filename
extension "{ext}"''')
            sys.exit(1)
    # check if valid language
    utility.valididate_language(language)
    if not mainclass:
        mainclass = utility.guess_mainclass(language, _files)
    # Finally, submit the solution
    kattis.submit_solution(_files, problemid,
                           language, mainclass,
                           tag, force)


if __name__ == '__main__':
    main()
