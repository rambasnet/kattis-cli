"""Tester module for KattisKitten.
"""

from typing import Any, List, Dict
import glob
import time
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
# from rich import print
from rich.live import Live
from rich.align import Align
from rich import box
from rich.prompt import Confirm

from kattis_cli import kattis
from kattis_cli.utils import run_program, utility


def test_samples(
        problemid: str,
        loc_language: str,
        mainclass: str,
        problem_root_folder: str,
        files: List[str],
        lang_config: Dict[Any, Any]
) -> None:
    """Tests a problem by running all the .in files in
    the problem folder and comparing the output to the .ans files.

    Args:
        problem (str): problemid
        loc_language (str): programming language
        mainclass (str): main class
        problem_root_folder (str): root folder where this problem is located
        files (List[str]): List of files
        lang_config (Dict[Any, Any]): language config
    """
    console = Console()
    # print(f"Main file: {mainfile}")
    # config_data = config.parse_config(language)

    # console.print(extensions)
    # UI Table Header ---

    table = Table(show_header=True,
                  header_style="bold blue",
                  show_lines=True,
                  show_footer=False)
    table.box = box.SQUARE
    table_centered = Align.center(table)

    # console.print(table)
    # Find all .in files in the problem folder
    sep = os.path.sep
    in_files = glob.glob(f"{problem_root_folder}{sep}data{sep}*.in")
    if not in_files:
        console.print(f"Sample data folder: {problem_root_folder}{sep}data",
                      style="bold blue")
        console.print("No sample input files found!", style="bold red")
        exit(1)
    in_files.sort()
    # check if language needs to be compiled
    if lang_config['compile']:
        ex_code, ans, error = run_program.compile_program(lang_config, files)
        if ex_code != 0:  # compilation error; exit code
            console.print(error, style='bold red')
            exit(1)
        # mainfile = './a.out'
        console.print('Compiled successfully!', style='bold green')
        # console.print('Output file: a.out', style='bold green')
    # console.print(in_files)
    count = 0
    total = len(in_files)
    console.clear()
    title = f"[not italic bold blue]👷‍ Testing {mainclass} "
    title += f" using {loc_language} 👷‍[/]"
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
            code, ans, error = run_program.run(lang_config, mainclass, in_file)
            expected = expected.strip()
            if code != 0:
                ans = error
            # console.print(f"{ans=} {error=}")
            if expected == ans.encode('utf-8').strip():
                result = "[bold green]✅[/bold green]"
                count += 1
            else:
                result = "[bold red]❌[/bold red]"

            # UI Table Row ---
            in_filename = Path(in_file).parts[-1]
            out_filename = Path(out_file).parts[-1]
            # with beat(10):
            time.sleep(0.1)
            table.add_row(in_filename,
                          input_content.decode('utf-8'),
                          out_filename,
                          expected.decode('utf-8'),
                          ans,
                          result)
            if code != 0 and 'SyntaxError: ' in error:
                table.columns[4].style = 'bold red'
                break

    console.print(
        f"Sample data folder: {problem_root_folder}{sep}data",
        style="bold blue")
    console.print(f'Total {total} input/output sample(s) found.')
    console.print(f"{count}/{total} tests passed.")
    if count < total:
        console.print("Check the output columns for differences.")
        console.print("Keep trying!")
    else:
        console.print(
            "Awesome... Time to submit it to :cat: Kattis! :cat:",
            style="bold green")
        if Confirm.ask("Submit to Kattis?", default=True):
            kat_language = utility.LOCAL_TO_KATTIS.get(loc_language, '')
            kattis.submit_solution(files, problemid,
                                   kat_language, mainclass,
                                   tag="", force=True)
