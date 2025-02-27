"""Module for language utilities.
"""

from typing import List, Dict, Any
import sys
import os
import re
from pathlib import Path
from rich.console import Console
from kattis_cli.utils import config
from kattis_cli.utils.utility import find_problem_root_folder


LANGUAGE_GUESS = {
    '.c': 'c',
    '.c++': 'cpp',
    '.cc': 'cpp',
    '.c#': 'csharp',
    '.cpp': 'cpp',
    '.cs': 'csharp',
    '.cxx': 'cpp',
    '.cbl': 'cobol',
    '.cob': 'cobol',
    '.cpy': 'cobol',
    '.fs': 'fsharp',
    '.go': 'go',
    '.hs': 'haskell',
    '.java': 'java',
    '.js': 'nodejs',
    '.ts': 'typescript',
    '.kt': 'kotlin',
    '.lisp': 'lisp',
    '.cl': 'lisp',
    '.m': 'objective-c',
    '.ml': 'ocaml',
    '.pas': 'pascal',
    '.php': 'php',
    '.pl': 'prolog',
    '.py': 'python3',
    '.rb': 'ruby',
    '.rs': 'rust',
    '.scala': 'scala',
    '.f90': 'fortran',
    '.f': 'fortran',
    '.for': 'fortran',
    '.sh': 'bash',
    '.apl': 'apl',
    '.ss': 'gerbil',
    '.jl': 'julia',
    '.vb': 'vb',
    '.dart': 'dart',
    '.zig': 'zig',
    '.swift': 'swift',
    '.nim': 'nim',
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
    'Python 3',
    'Ruby',
    'Rust',
    'TypeScript',
    'Zig'
}

# mapping is used for .kattis-cli.toml file configuration
LOCAL_TO_KATTIS = {
    'python3': 'Python 3',
    'java': 'Java',
    'cpp': 'C++',
    'c++': 'C++',
    'nodejs': 'JavaScript (Node.js)',
    'typescript': 'TypeScript',
    'csharp': 'C#',
    'kotlin': 'Kotlin',
    'scala': 'Scala',
    'rust': 'Rust',
    'pascal': 'Pascal',
    'go': 'Go',
    'haskell': 'Haskell',
    'ruby': 'Ruby',
    'php': 'PHP',
    'lisp': 'Common Lisp',
    'fortran': 'Fortran',
    'bash': 'Bash',
    'apl': 'APL',
    'gerbil': 'Gerbil',
    'julia': 'Julia',
    'vb': 'Visual Basic',
    'dart': 'Dart',
    'zig': 'Zig',
    'swift': 'Swift',
    'nim': 'Nim',
    'ocaml': 'OCaml',
    'fsharp': 'F#',
    'cobol': 'COBOL',
    'prolog': 'Prolog',
    'objective-c': 'Objective-C',
    'c': 'C',
    'c#': 'C#'
}


def guess_language(ext: str, files: List[str]) -> str:
    """Guess the language.

    Args:
        ext (str): File extension.
        files (List[str]): Tuple of files.

    Returns:
        str: guessed language
    """
    if ext == ".C":
        return "cpp"
    ext = ext.lower()
    if ext == ".h":
        if any(f.endswith(".c") for f in files):
            return "c"
        else:
            return "cpp"
    if ext == ".py":
        return "python3"
    return LANGUAGE_GUESS.get(ext, '')


# flake8: noqa: C901
def guess_mainfile(
        kat_language: str,
        files: List[str],
        problemid: str,
        lang_config: Dict[Any, Any]) -> Any:
    """Guess the main file.

    Args:
        kat_language (str): programming language name used by Kattis
        files (List[str]): Tuple of files

    Returns:
        str: main file
    """
    if len(files) == 1:
        return files[0]
    # check .kattis-cli.toml file
    if 'mainfile' in lang_config:
        return lang_config['mainfile'].replace(('{problemid}'), problemid)
    for filename in files:
        if os.path.splitext(os.path.basename(filename))[0] in ['main', 'Main']:
            return filename
        if problemid and os.path.splitext(
                os.path.basename(filename))[0] == problemid:
            return filename
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                conts = f.read()
                if kat_language in [
                        'Java', 'Rust', 'Scala', 'Kotlin'] and re.search(
                        r' main\s*\(', conts):
                    return filename
                if kat_language == 'Pascal' and re.match(
                        r'^\s*[Pp]rogram\b', conts):
                    return filename
        except IOError:
            pass
    # main file is the one with problemid
    return files[0]


def guess_mainclass(
        problemid: str,
        kat_language: str,
        files: List[str],
        lang_config: Any) -> Any:
    """Guess the main class.

    Args:
        kat_language (str): programming language name used by Kattis
        files (List[str]): List of files to guess mainclass from

    Returns:
        str: mainclass name or empty string
    """
    if kat_language in GUESS_MAINFILE and len(files) > 1:
        return os.path.basename(
            guess_mainfile(
                kat_language,
                files,
                problemid,
                lang_config))
    if kat_language in GUESS_MAINCLASS:
        mainfile = os.path.basename(
            guess_mainfile(
                kat_language,
                files,
                problemid,
                lang_config))
        name = os.path.splitext(mainfile)[0]
        if kat_language == 'Kotlin':
            return name[0].upper() + name[1:] + 'Kt'
        return name
    return ''


def validate_language(loc_language: str) -> bool:
    """Check if valid language.

    Args:
        loc_language (str): programming language provided by user

    Returns:
        bool: True if valid language, exit otherwise.
    """
    if loc_language in LOCAL_TO_KATTIS:
        return True
    console = Console()
    console.print(f'Invalid language: "{loc_language}"', style='bold red')
    console.print('Valid languages are:', style='bold green')
    for lang in sorted(LOCAL_TO_KATTIS.keys()):
        console.print(f'\t\t - {lang}')
    exit(1)


def valid_extension(file: str) -> bool:
    """Check if valid extension.

    Args:
        file (str): File name.

    Returns:
        bool: True if valid extension, False otherwise.
    """
    if os.path.isfile(file):
        ext = os.path.splitext(file)
        if len(ext) != 2:
            return False
        return ext[1] in LANGUAGE_GUESS
    return False


# flake8: noqa: C901
def update_args(problemid: str,
                loc_language: str,
                mainclass: str,
                files: List[str]) -> Any:
    """Check if problemid, language, mainclass, and program files are valid.

    Args:
        problemid (str): problemid
        loc_language (str): programming language provided by user
        mainclass (str): main class
        files (List[str]): List of files

    Returns:
        Tuple[str]: Update problemid, kattis_language, mainclass, and files
    """

    console = Console()
    if not files:
        files = get_coding_files()
    # check if problemid is given
    # if not problemid:
    cur_folder = Path.cwd()
    root_folder = Path.cwd()
    if not problemid:
        for f in files:
            try:
                root_folder = find_problem_root_folder(
                    cur_folder, f.lower())
                # if not problemid:
                problemid = root_folder.name
                break
            except FileNotFoundError:
                # print(ex)
                pass
    if not problemid:
        try:
            root_folder = find_problem_root_folder(
                cur_folder, '*.yaml')
            problemid = root_folder.name
        except FileNotFoundError:
            console.print(f'''No problemid specified and I failed to guess
problemid and root problem folder from filename(s) and cwd: {cur_folder}.''',
                          style='bold red')
            sys.exit(1)
    # check if language
    if not loc_language:
        _, ext = os.path.splitext(os.path.basename(files[0]))
        # Guess language from files
        loc_language = guess_language(ext, files)
        if not loc_language:
            console.print(f'''\
No language specified, and I failed to guess language from
filename extension "{ext}"''')
            sys.exit(1)
    # check if valid language
    validate_language(loc_language)
    lang_config = config.parse_config(loc_language)
    kat_language = LOCAL_TO_KATTIS[loc_language]
    if not mainclass:
        mainclass = guess_mainclass(
            problemid, kat_language, files, lang_config)
    # print(f'Returning...{problemid=} {language=} {mainclass=} {files=}')
    return problemid, loc_language, mainclass, files, root_folder, lang_config


def get_coding_files() -> List[str]:
    """Get coding files from current directory.

    Returns:
        List[str]: List of coding files.
    """
    cur_folder = str(Path.cwd())
    console = Console()
    files = [
        f for f in os.listdir(cur_folder) if valid_extension(f)]
    if not files:
        console.print(
            'No source file(s) found in the current folder!',
            style='bold red')
        exit(1)
    return files
