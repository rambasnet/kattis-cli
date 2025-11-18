"""Solution tester module for Kattis.

Provides a SolutionTester class and a module-level `test_samples`
delegator for backward compatibility with the previous procedural API.
"""

from typing import Any, List, Dict, Optional
from math import inf
import glob
import time
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.align import Align
from rich import box
from rich.prompt import Confirm
from rich.markup import escape

from kattis_cli import kattis
from kattis_cli.utils import languages, run_program, utility


class SolutionTester:
    """Encapsulates testing of solutions using sample data.

    Accepts optional collaborators to make testing easier to mock in
    unit tests.
    """

    def __init__(
        self,
        client: Optional[Any] = None,
        download_manager: Optional[Any] = None,
    ) -> None:
        """Create a SolutionTester.

        Args:
            client: Optional client or module providing submit_solution.
            download_manager: Optional download manager instance.
        """

        self.client = client or kattis
        self.download_manager = download_manager

    def test_samples(
            self,
            problemid: str,
            loc_language: str,
            mainclass: str,
            problem_root_folder: str,
            files: List[str],
            lang_config: Dict[Any, Any],
            accuracy: float = inf
    ) -> None:
        """Run the sample tests for a solution.

        This mirrors the previous procedural `test_samples` function but
        is encapsulated on a class to allow dependency injection for
        easier testing.
        """
        console = Console()

        table = Table(show_header=True,
                      header_style="bold blue",
                      show_lines=True,
                      show_footer=False)
        table.box = box.SQUARE
        table_centered = Align.center(table)

        sep = os.path.sep
        in_files = glob.glob(f"{problem_root_folder}{sep}data{sep}*.in")
        if not in_files:
            data_path = f"{problem_root_folder}{sep}data"
            console.print(data_path, style="bold blue")
            console.print("No sample input files found!", style="bold red")
            exit(1)
        in_files.sort()
        if lang_config['compile']:
            ex_code, ans, error = run_program.compile_program(
                lang_config,
                files,
            )
            if ex_code != 0:  # compilation error; exit code
                console.print(escape(error), style='bold red')
                exit(1)
            console.print('Compiled successfully!', style='bold green')

        count = 0
        total = len(in_files)
        console.clear()
        title = f"[not italic bold blue]👷‍ Testing {mainclass} "
        main_src_file = next((f for f in files if f.endswith(mainclass)), None)
        if not main_src_file:
            main_src_file = mainclass

        title += f" using {loc_language} 👷‍[/]"
        table.title = title
        with Live(table_centered, console=console,
                  screen=False, refresh_per_second=10):
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
                try:
                    with open(out_file, 'rb') as f:
                        expected = f.read()
                        expected.replace(b'\r\n', b'\n')
                except FileNotFoundError:
                    try:
                        out_file = in_file.replace('.in', '.out')
                        with open(out_file, 'rb') as f:
                            expected = f.read()
                            expected.replace(b'\r\n', b'\n')
                    except FileNotFoundError:
                        expected = b"No .ans or .out file found!"
                code, ans, error = run_program.run(
                    lang_config,
                    main_src_file,
                    in_file,
                )
                if code != 0:
                    ans = error

                if utility.check_answer(expected.decode('utf-8'),
                                        ans, accuracy):
                    result = "[bold green]✅[/bold green]"
                    count += 1
                else:
                    result = "[bold red]❌[/bold red]"

                in_filename = Path(in_file).parts[-1]
                if b"No .ans or .out file found!" == expected:
                    out_filename = "N/A"
                else:
                    out_filename = Path(out_file).parts[-1]
                time.sleep(0.1)
                table.add_row(in_filename,
                              input_content.decode('utf-8'),
                              out_filename,
                              escape(expected.decode('utf-8')),
                              escape(ans),
                              result)
                if code != 0 and 'SyntaxError: ' in error:
                    table.columns[4].style = 'bold red'
                    break

        data_path = f"{problem_root_folder}{sep}data"
        console.print(data_path, style="bold blue")
        console.print(f'Total {total} input/output sample(s) found.')
        console.print(f"{count}/{total} tests passed.")
        if count < total:
            console.print("Check the output columns for differences.")
            console.print("Keep trying!")
        else:
            console.print(
                "Awesome... Time to submit it to :cat: Kattis! :cat:",
                style="bold green",
            )
            if Confirm.ask("Submit to Kattis?", default=True):
                kat_language = (
                    languages.LOCAL_TO_KATTIS.get(loc_language, '')
                )
                self.client.submit_solution(
                    files,
                    problemid,
                    kat_language,
                    mainclass,
                    tag="",
                    force=True,
                )


# Default manager for module-level compatibility
_tester = SolutionTester()


def test_samples(
        problemid: str,
        loc_language: str,
        mainclass: str,
        problem_root_folder: str,
        files: List[str],
        lang_config: Dict[Any, Any],
        accuracy: float = inf
) -> None:
    """Module-level wrapper delegating to the :class:`SolutionTester`.

    Keeps the original procedural API for callers that import
    `test_samples` directly from the module.
    """

    return _tester.test_samples(problemid, loc_language, mainclass,
                                problem_root_folder, files, lang_config,
                                accuracy)
