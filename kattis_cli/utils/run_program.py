"""Run the program with the given input file and return the output.
"""

import subprocess
from typing import Tuple, List, Dict, Any


def compile_program(
        lang_config: Dict[Any, Any], files: List[str]) -> Tuple[int, str, str]:
    """Compile Program.

    Args:
        lang_config (Dict[Any, Any]): language config
        files (List[str]): List of files
    """
    command = lang_config['compile'].split()
    command.extend(files)
    # print(f'{command=}')
    # print(f'{files}')
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


def run(lang_config: Dict[Any, Any],
        mainclass: str,
        input_file: str) -> Tuple[int, str, str]:
    """Run the program with the given input file and return the output.

    Args:
        lang_config (str): programming language config
        mainclass (str): main file
        input_file (str): input file

    Returns:
        Tuple[str, str]: program output and error
    """

    program = lang_config['execute'].replace("{mainfile}", mainclass).split()
    # print(f'{program=}')
    code, ans, error = execute(program, input_file)
    return code, ans, error


def execute(command: List[str], in_file: str) -> Tuple[int, str, str]:
    """Execute the command with the given input file and return the output.

    Args:
        files (List[str]): List of files
    """
    # print(f'{command=}')

    # Set the g++ command and its arguments in a list
    # command = [compiler, '-std=c++11', '-o', 'output_program', 'cold.cpp']
    # command = [python3, 'main.py']

    # Use Popen to execute the command
    filein = open(in_file, 'r', encoding='utf-8')

    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=filein)

    # Wait for the process to finish and get the output and errors
    stdout, stderr = process.communicate()

    # Print the output and errors
    output = stdout.decode('utf-8')
    error = stderr.decode('utf-8')
    return process.returncode, output, error
