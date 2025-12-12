""" Main module for the kattis_cli package.

Change the __version__ to match in pyproject.toml
"""
__version__ = '1.2.3'

from math import inf
import os
from typing import Tuple
from rich.console import Console
import click
import requests
from trogon import tui
import kattis_cli.download as download
import kattis_cli.ui as ui
import kattis_cli.solution_tester as solution_tester
import kattis_cli.kattis as kattis
import kattis_cli.utils.languages as languages
import kattis_cli.kattis_setup as kattis_setup
import kattis_cli.template as template


@tui()
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
        f"Downloading metadata: [bold blue]{problemid}[/bold blue]")
    try:
        download.load_problem_metadata(problemid)
    except requests.exceptions.InvalidURL:
        console.print(
            f"Problem ID: [bold red]{problemid}[/bold red] not found.")
    else:
        console.print(
            f"Downloading samples: [bold blue]{problemid}[/bold blue]")
        try:
            download.download_sample_data(problemid)
        except requests.exceptions.InvalidURL:
            console.print(
                f"Problem ID: [bold red]{problemid}[/bold red] metadata \
                    not found.")
        else:
            console.print(
                f"Downloaded samples and metadata: \
    [bold blue]{problemid}[/bold blue]")


@main.command(help='Show problem metadata.')
@click.option('-p', '--problemid', default='', help='Problem ID.')
def info(problemid: str) -> None:
    """Display problem metadata.
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

    solution_tester.test_samples(
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


@main.command(help='Create a template file for a problem.')
@click.option('-l', '--language', default='python3',
              help='Programming language (default: python3)')
@click.option('-p', '--problemid', default=None,
              help='Problem ID (default: parent directory name)')
@click.option('-s', '--src', is_flag=True, default=False,
              help='Create src layout structure')
def template_cmd(language: str, problemid: str, src: bool) -> None:
    """Create a template file.
    """
    if not problemid:
        problemid = os.path.basename(os.getcwd())

    template.create_template(language, problemid, src)


if __name__ == '__main__':
    main()
