"""Runs a C++ file and returns the output."
"""

from typing import List, Tuple
import subprocess
import selectors
from kattis_cli.utils import config


def compile_cpp(files: List[str]) -> Tuple[int, str, str]:
    """Compile the C++ files.

    Args:
        files (List[str]): List of files
    """
    cpp_config = config.parse_config('cpp')
    command = [cpp_config['compiler']]
    command.extend(cpp_config['compiler_flags'].split())
    command.extend(files)
    # print(f'{command=}')

    # Set the g++ command and its arguments in a list
    # command = [compiler, '-std=c++11', '-o', 'output_program', 'cold.cpp']

    # Use Popen to execute the command
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    # Wait for the process to finish and get the output and errors
    stdout, stderr = process.communicate()

    # Print the output and errors
    output = stdout.decode('utf-8')
    error = stderr.decode('utf-8')
    return process.returncode, output, error


def run(program: str, input_file: str) -> Tuple[str, str]:
    """Run a C++ file and returns the output.

    Args:
        mainfile (str): file with main function
        input_content (bytes): _description_

    Returns:
        Tuple[str, str]: _description_
    """
    filein = open(input_file, 'r', encoding='utf-8')
    # first compile the files
    p = subprocess.Popen(
        [program], stdout=subprocess.PIPE,
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
