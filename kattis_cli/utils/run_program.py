"""Run the program with the given input file and return the output.
"""

import subprocess
from typing import Tuple, List

from . import config
from . import utility


def run(language: str, main_program: str,
        input_file: str) -> Tuple[int, str, str]:
    """Run the program with the given input file and return the output.

    Args:
        language (str): programming language
        main_program (str): main file
        input_file (str): input file

    Returns:
        Tuple[str, str]: program output and error
    """

    test_language = utility.LOCAL_TEST_LANGUAGES.get(language, '')
    config_data = config.parse_config(test_language)
    program = config_data['compiler']
    # print(f'{program=} {language} {test_language}')
    if not program:
        raise NotImplementedError(
            f"Language {language} not supported.")
    if language.strip().lower() == 'c++':
        code, ans, error = execute(['./a.out'], input_file)
    else:
        code, ans, error = execute([program, main_program], input_file)
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
