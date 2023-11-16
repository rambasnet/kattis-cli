"""Tester module for KattisKitten.
"""

from typing import Generator, List
from contextlib import contextmanager
import glob
import time
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
# from rich import print
from rich.live import Live
from rich.align import Align
from rich import box

from .utils import utility
from . import config
from .utils import run_python
from . import kattis

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


def test_samples(
        problemid: str,
        language: str,
        mainclass: str,
        problem_root_folder: str,
        files: List[str],
        ) -> None:
    """Tests a problem by running all the .in files in
    the problem folder and comparing the output to the .ans files.

    Args:
        problem (str): problemid
        language (str): programming language
        mainclass (str): main class
        problem_root_folder (str): root folder where this problem is located
        files (List[str]): List of files
    """
    console = Console()
    config_data = config.parse_config(language)

    # console.print(extensions)
    # UI Table Header ---

    table = Table(show_header=True,
                  header_style="bold blue",
                  show_lines=True,
                  show_footer=False)
    table.box = box.SQUARE
    table_centered = Align.center(table)

    # console.print(table)

    if not mainclass:
        mainclass = config_data['mainclass'].replace('<problemid>', problemid)
    # Find all .in files in the problem folder
    sep = os.path.sep
    in_files = glob.glob(f"{problem_root_folder}{sep}data{sep}*.in")
    if not in_files:
        console.print(f"Sample data folder: {problem_root_folder}{sep}data", style="bold blue")
        console.print("No sample input files found!", style="bold red")
        exit(1)
    in_files.sort()
    #console.print(in_files)
    count = 0
    total = len(in_files)
    console.clear()
    title = f"[not italic bold blue]👷‍ Testing {mainclass} "
    title += f" using {language} 👷‍[/]"
    compiler_error_checked = False
    table.title = title
    with Live(table_centered, console=console,
              screen=False, refresh_per_second=10):
        # with beat(10):
        # with beat(10):
        table.add_column(
            "Input File",
            justify="center",
            style="cyan",
            no_wrap=False)
        table.add_column(
            "Sample Input",
            justify="left",
            style="cyan",
            no_wrap=False)
        table.add_column(
            "Output File",
            justify="center",
            style="cyan",
            no_wrap=False)
        table.add_column(
            "Expected Output",
            justify="left",
            style="cyan",
            no_wrap=False)
        table.add_column(
            "Program Output",
            justify="left",
            style="cyan",
            no_wrap=False)
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
            if language.strip().lower() in ['python', 'python 3', 'python3']:
                output = run_python.run(str(mainclass), input_content)
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
            in_filename = Path(in_file).parts[-1]
            out_filename = Path(out_file).parts[-1]
            #with beat(10):
            time.sleep(0.1)
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
    
    console.print(f"Sample data folder: {problem_root_folder}{sep}data", style="bold blue")
    console.print(f'Total {total} input/output sample(s) found.')
    console.print(f"{count}/{total} tests passed.")
    if count < total:
        console.print("Check the output columns for details.")
        console.print("Keep trying!")
    else:
        console.print("Awesome... Time to submit it to :cat: Kattis! :cat:", style="bold green")
        console.print("Submit to Kattis? y/n: ", style="bold blue", end="")
        ans = input()
        if ans.lower() == 'y':
            kattis.submit_solution(files, problemid,
                                   language, mainclass,
                                   tag="", force=True)
