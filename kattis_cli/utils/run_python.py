"""Runs a python file and returns the output."
"""

import subprocess
import textwrap


def run(file: str, input_content: bytes) -> str:
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
