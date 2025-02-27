""" Main module for the kattis_cli package.
This is the main.py file for the kattis_cli package.

Change the contents here instead of main.py.
build.sh script copies the contents of this file to main.py.

Change the __version__ to match in pyproject.toml
Has to be higher than the pypi version.
"""
__version__ = '1.0.4'

from math import inf
from typing import Tuple
from rich.console import Console
import click
import requests
import kattis_cli.download as download
import kattis_cli.ui as ui
import kattis_cli.test_solution as test_solution
import kattis_cli.kattis as kattis
import kattis_cli.utils.languages as languages
import kattis_cli.kattis_setup as kattis_setup


@click.group()
@click.version_option(version=__version__, prog_name='kattis-cli')
def main() -> None:
    """
    CLI for downloading, testing and submitting Kattis problems.
    """
    pass


@main.command(help='Download sample data & metadata.')
@click.argument('problemid')
def get(problemid: str) -> None:
    """Command Line Interface for Kattis.
    """
    console = Console()
    console.print(
        f"Downloading samples: [bold blue]{problemid}[/bold blue]")
    try:
        download.download_sample_data(problemid)
    except requests.exceptions.InvalidURL:
        console.print(
            f"""Sample data for Problem ID: [bold blue]
            {problemid}[/bold blue] not found.")
            """)
    console.print(
        f"Downloading metadata: [bold blue]{problemid}[/bold blue]")
    download.load_problem_metadata(problemid)


@main.command(help='Show problem metadata.')
@click.option('-p', '--problemid', default='', help='Problem ID.')
def info(problemid: str) -> None:
    """Display problem metada.
    """
    ui.show_problem_metadata(problemid)


@main.command(help='Test solution with sample files.')
@click.option('-p', '--problemid', default='', help='Problem ID')
@click.option('-l', '--language', default='', help='Sets language')
@click.option('-m', '--mainclass', default='', help='Sets mainclass/mainfile')
@click.option('-a', '--accuracy', default=inf,
              help='Decimal places for float comparison')
@click.argument('files', nargs=-1, required=False)
def test(
        problemid: str,
        language: str,
        mainclass: str,
        accuracy: float,
        files: Tuple[str]) -> None:
    """Test solution with sample files.
    """
    problemid, loc_language, mainclass, _files, root_folder, lang_config = \
        languages.update_args(problemid, language, mainclass, list(files))
    # print('After - ', f'{problemid=} {language=} {mainclass=} {_files=}')
    # lang_config = config.parse_config(language)
    if not mainclass:
        mainclass = languages.guess_mainfile(
            language, _files, problemid, lang_config)

    test_solution.test_samples(
        problemid,
        loc_language,
        mainclass,
        root_folder,
        _files,
        lang_config,
        accuracy)


@main.command(help='Submit a solution to Kattis.')
@click.option('-p', '--problemid', default='',
              help='Which problem to submit to.')
@click.option('-l', '--language', default='', help='Sets language')
@click.option('-m', '--mainclass', default='', help='Sets mainclass/mainfile.')
@click.option("-t", '--tag', help="Disable all prompts",
              flag_value=True, default=False)
@click.option('-f',
              '--force',
              help="Force, no confirmation prompt before submission",
              flag_value=True,
              default=False)
@click.argument('files', nargs=-1, required=False)
def submit(problemid: str, language: str,
           mainclass: str, tag: str, force: bool,
           files: Tuple[str]) -> None:
    """Submit a solution to Kattis.
    """
    problemid, language, mainclass, _files, _, lang_config = \
        languages.update_args(
            problemid, language, mainclass, list(files))
    # Finally, submit the solution
    # print(f'{problemid=} {language=} {mainclass=} {tag=} {force=} {_files=}')
    if not mainclass:
        mainclass = languages.guess_mainfile(
            language, _files, problemid, lang_config)
    kat_lang = languages.LOCAL_TO_KATTIS[language]
    kattis.submit_solution(_files, problemid,
                           kat_lang, mainclass,
                           tag, force)


@main.command(help='Setup Kattis CLI.')
def setup() -> None:
    """Setup Kattis CLI.
    """
    kattis_setup.setup()


if __name__ == '__main__':
    main()
