"""Module for language utilities.
"""
from typing import List, Union
import os
import re
from pathlib import Path
from rich.console import Console


LANGUAGE_GUESS = {
    '.c': 'C',
    '.c++': 'C++',
    '.cc': 'C++',
    '.c#': 'C#',
    '.cpp': 'C++',
    '.cs': 'C#',
    '.cxx': 'C++',
    '.cbl': 'COBOL',
    '.cob': 'COBOL',
    '.cpy': 'COBOL',
    '.fs': 'F#',
    '.go': 'Go',
    '.hs': 'Haskell',
    '.java': 'Java',
    '.js': 'JavaScript (Node.js)',
    '.ts': 'TypeScript',
    '.kt': 'Kotlin',
    '.lisp': 'Common Lisp',
    '.cl': 'Common Lisp',
    '.m': 'Objective-C',
    '.ml': 'OCaml',
    '.pas': 'Pascal',
    '.php': 'PHP',
    '.pl': 'Prolog',
    '.py': 'Python 3',
    '.pyc': 'Python 3',
    '.rb': 'Ruby',
    '.rs': 'Rust',
    '.scala': 'Scala',
    '.f90': 'Fortran',
    '.f': 'Fortran',
    '.for': 'Fortran',
    '.sh': 'Bash',
    '.apl': 'APL',
    '.ss': 'Gerbil',
    '.jl': 'Julia',
    '.vb': 'Visual Basic',
    '.dart': 'Dart',
    '.zig': 'Zig',
    '.swift': 'Swift',
    '.nim': 'Nim',
}

GUESS_MAINCLASS = {'Java', 'Kotlin', 'Scala'}
GUESS_MAINFILE = {
    'APL',
    'Bash',
    'Dart',
    'Gerbil',
    'JavaScript (Node.js)',
    'Julia',
    'Common Lisp',
    'Pascal',
    'PHP',
    'Python 2',
    'Python 3',
    'Ruby',
    'Rust',
    'TypeScript',
    'Zig'}


def guess_language(ext: str, files: List[str]) -> str:
    """Guess the language.

    Args:
        ext (str): File extension.
        files (List[str]): Tuple of files.

    Returns:
        str: guessed language
    """
    if ext == ".C":
        return "C++"
    ext = ext.lower()
    if ext == ".h":
        if any(f.endswith(".c") for f in files):
            return "C"
        else:
            return "C++"
    if ext == ".py":
        if is_python2(files):
            return "Python 2"
        else:
            return "Python 3"
    return LANGUAGE_GUESS.get(ext, '')


def is_python2(files: List[str]) -> bool:
    """Check if python2.

    Args:
        files (List[str]): Tuple of files.

    Returns:
       bool: True if python2, False otherwise.
    """
    python2 = re.compile(r'^\s*\bprint\b *[^ \(\),\]]|\braw_input\b')
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for index, line in enumerate(f):
                    # print(index, line)
                    if index == 0 and line.startswith('#!'):
                        if 'python2' in line:
                            return True
                        if 'python3' in line:
                            return False
                    if python2.search(line.split('#')[0]):
                        return True
        except IOError:
            return False
    return False


def guess_mainfile(language: str, files: List[str]) -> str:
    """Guess the main file.

    Args:
        language (str): programming language
        files (List[str]): Tuple of files

    Returns:
        str: main file
    """
    for filename in files:
        if os.path.splitext(os.path.basename(filename))[0] in ['main', 'Main']:
            return filename
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                conts = f.read()
                if language in [
                        'Java', 'Rust', 'Scala', 'Kotlin'] and re.search(
                        r' main\s*\(', conts):
                    return filename
                if language == 'Pascal' and re.match(
                        r'^\s*[Pp]rogram\b', conts):
                    return filename
        except IOError:
            pass
    return files[0]


def guess_mainclass(language: str, files: List[str]) -> str:
    """Guess the main class.

    Args:
        language (str): programming language
        files (Tuple[str]): Tuple of files

    Returns:
        str: main class
    """
    if language in GUESS_MAINFILE and len(files) > 1:
        return os.path.basename(guess_mainfile(language, files))
    if language in GUESS_MAINCLASS:
        mainfile = os.path.basename(guess_mainfile(language, files))
        name = os.path.splitext(mainfile)[0]
        if language == 'Kotlin':
            return name[0].upper() + name[1:] + 'Kt'
        return name
    return ''


def valididate_language(language: str) -> bool:
    """Check if valid language.

    Args:
        language (str): programming language

    Returns:
        bool: True if valid language, exit otherwise.
    """
    if language in LANGUAGE_GUESS.values():
        return True
    console = Console()
    console.print(f'Invalid language: "{language}"', style='bold red')
    console.print('Valid languages are:', style='bold green')
    for lang in sorted(list(set(LANGUAGE_GUESS.values()))):
        console.print(f'\t\t - {lang}')
    exit(1)


def valid_extension(file: str) -> bool:
    """Check if valid extension.

    Args:
        ext (str): File extension.

    Returns:
        bool: True if valid extension, exit otherwise.
    """
    if os.path.isfile(file):
        ext = os.path.splitext(file)
        if len(ext) != 2:
            return False
        return ext[1] in LANGUAGE_GUESS
    return False


def find_problem_root_folder(
    directory_path: Union[str, Path],
    filename: str
) -> Path:
    """Find the root problem folder given a directory path and filename.

    Args:
        directory_path (Union[str, Path]): String or Path
            object of directory path
        filename (str): filename to search for
            including wildcard pattern

    Returns:
        Path: Path object of the root problem folder
    """

    def _check_file_match_folder(path: Path, filename: str) -> bool:
        """ Check folder is same name as the filename given
        filename including wildcard.

        Args:
            path (Path): Path object of directory path
            filename (str): filename to search for
                including wildcard pattern
        Returns:
            bool: True if path exists, False otherwise
        """
        for file in path.glob(filename):
            name, _ = os.path.splitext(file.name)
            # print(file.name, path.parts[-1], file.name[:len(ext[1])+1])
            folder_name = path.parts[-1]
            if file.is_file() and name == folder_name:
                return True
        return False

    # print('path', directory_path, filename, file=sys.stderr)
    cur_path = Path(directory_path)
    if _check_file_match_folder(cur_path, filename):
        return cur_path
    for parent in Path(directory_path).parents:
        # print('parent', parent, file=sys.stderr)
        if _check_file_match_folder(parent, filename):
            return parent
    raise FileNotFoundError("Error: Problem root folder not found.")
