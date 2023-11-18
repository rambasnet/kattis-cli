"""Runs a python file and returns the output."
"""

from typing import Tuple
import subprocess
import selectors
import textwrap


def run(mainfile: str, input_file: str) -> Tuple[str, str]:
    """_summary_

    Args:
        mainfile (str): _description_
        input_content (bytes): _description_

    Returns:
        Tuple[str, str]: _description_
    """
    filein = open(input_file, 'r', encoding='utf-8')
    p = subprocess.Popen(
        ["python", mainfile], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, stdin=filein
    )
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)  # type: ignore
    sel.register(p.stderr, selectors.EVENT_READ)  # type: ignore
    ans = ''
    error = ''
    done = False
    while not done:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()  # type: ignore
            if not data:
                done = True
                break
            if key.fileobj is p.stdout:
                # print(data, end="")
                ans = data
            else:
                # print(data, end="", file=sys.stderr)
                error = data
    return ans, error


def run_old(file: str, input_content: bytes) -> str:
    """Runs a python file and returns the output."""
    # print(f'{file=}')
    try:
        output = subprocess.check_output(
            ['python3', file], stderr=subprocess.STDOUT, input=input_content)
        return output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        # console = Console()
        # print('error', e.output)
        # console.print_exception(show_locals=True)
        # output = e.output.decode("utf-8")
        stdout = e.stdout.decode("utf-8").strip()
        # console.print(e.stdout.decode("utf-8"), style='red')
        wraped_text = textwrap.wrap(stdout.replace("\n", ''), 40)
        if stdout.find('SyntaxError') != -1:
            return '** Syntax Error **\n' + '\n'.join(wraped_text)
        else:
            return '\n'.join(wraped_text)
