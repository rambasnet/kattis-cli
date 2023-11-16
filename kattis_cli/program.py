"""Tester module for KattisKitten.
"""

from typing import Generator
from contextlib import contextmanager
import glob
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
# from rich import print
from rich.live import Live
from rich.align import Align
from rich import box

from . import download
from . import config
from .utils import run_python

BEAT_TIME = 0.04


@contextmanager
def beat(length: int = 1) -> Generator[None, None, None]:
    """Beat the heart.

    Args:
        length (int, optional): _description_. Defaults to 1.

    Yields:
        Generator[None, None, None]: yields None
    """
    yield
    time.sleep(length * BEAT_TIME)


def test_solution(
        problemid: str,
        language: str = 'python',
        main_file: str = "",
        show_result: bool = True) -> None:
    """Tests a problem by running all the .in files in
    the problem folder and comparing the output to the .ans files.

    Args:
        problem (str): problemid
        log (bool, optional): Defaults to True.

    Returns:
        bool: True if all tests passed, False otherwise.
    """

    console = Console()
    filename = "*.yaml"
    if problemid:
        filename = f"{problemid}.yaml"

    try:
        root_problem_folder = download.find_problem_root_folder(
            Path.cwd(), filename)
    except FileNotFoundError:
        root_problem_folder = Path.cwd().joinpath('cold')
        console.print(
            f"Problem [bold]{problemid}[/bold] not found.",
            style="red")
        # exit(1)
    config_data = config.parse_config(language)
    console.print(root_problem_folder)
    _ = config_data['file_extensions']
    _ = config_data['kattis_name']
    emoji = config_data['emoji']
    # console.print(extensions)
    # UI Table Header ---

    table = Table(show_header=True,
                  header_style="bold blue",
                  show_lines=True,
                  show_footer=False)
    table.box = box.SQUARE
    table_centered = Align.center(table)

    # End Table Header ---
    # console.print(table)

    # Find all .in files in the problem folder
    if not main_file:
        main_file = config_data['main_class'].replace('<problemid>', problemid)
    main_class = root_problem_folder.joinpath(main_file)
    # console.print(main_class)
    in_files = glob.glob(f"{root_problem_folder}/data/*.in")
    in_files.sort()
    # console.print(in_files)
    count = 0
    total = len(in_files)
    console.clear()
    title = f"[not italic bold blue]👷‍ Testing {main_file} "
    title += f" using {emoji} {language} {emoji} 👷‍[/]"
    compiler_error_checked = False
    with Live(table_centered, console=console,
              screen=False, refresh_per_second=20):
        # with beat(10):
        table.title = title
        # with beat(10):
        table.add_column(
            "Input File",
            justify="center",
            style="cyan",
            no_wrap=True)
        table.add_column(
            "Sample Input",
            justify="left",
            style="cyan",
            no_wrap=True)
        table.add_column(
            "Output File",
            justify="center",
            style="cyan",
            no_wrap=True)
        table.add_column(
            "Expected Output",
            justify="left",
            style="cyan",
            no_wrap=True)
        table.add_column(
            "Program Output",
            justify="left",
            style="cyan",
            no_wrap=True)
        table.add_column(
            "Result",
            justify="center",
            style="cyan",
            no_wrap=True)

        for in_file in in_files:
            with open(in_file, 'rb') as f:
                input_content = f.read()
                input_content.replace(b'\r\n', b'\n')  # Windows fix
            out_file = in_file.replace('.in', '.ans')
            with open(out_file, 'rb') as f:
                expected = f.read()
                expected.replace(b'\r\n', b'\n')
            # Run the program
            if language == 'python':
                output = run_python.run(str(main_class), input_content)
            else:
                raise NotImplementedError(
                    f"Language {language} not supported.")

            expected = expected.strip()

            if expected == output.encode('utf-8').strip():
                result = "[bold green]✅[/bold green]"
                count += 1
            else:
                result = "[bold red]❌[/bold red]"

            # UI Table Row ---
            in_filename = in_file.split('/')[-1]
            out_filename = out_file.split('/')[-1]
            with beat(10):
                table.add_row(in_filename,
                              input_content.decode('utf-8'),
                              out_filename,
                              expected.decode('utf-8'),
                              output,
                              result)
            if not compiler_error_checked:
                compiler_error_checked = True
                if output.startswith('** Syntax Error **'):
                    table.columns[4].style = 'bold red'
                    break
            # End Table Row ---
            # console.print(table)
            # console.clear()

    # console.clear()
    # clear screen
    # print('\033[H\033[J')
    # console.print(table)
    console.print(f"Total: {count}/{total} tests passed.")
    suggestion = 'Keep trying!' if count < total else \
        '🎉 Awesome... 🎉 Time to submit it to :cat: Kattis! :cat:'
    console.print(suggestion)
