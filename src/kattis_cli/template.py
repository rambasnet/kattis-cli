"""Module for generating project templates."""

import os
import shutil
from pathlib import Path
import importlib.resources as pkg_resources
from rich.console import Console


LANGUAGE_EXTENSIONS = {
    'c': '.c',
    'cpp': '.cpp',
    'csharp': '.cs',
    'cobol': '.cob',
    'fsharp': '.fs',
    'go': '.go',
    'haskell': '.hs',
    'java': '.java',
    'nodejs': '.js',
    'typescript': '.ts',
    'kotlin': '.kt',
    'lisp': '.lisp',
    'objective-c': '.m',
    'ocaml': '.ml',
    'pascal': '.pas',
    'php': '.php',
    'prolog': '.pl',
    'python': '.py',
    'python3': '.py',
    'ruby': '.rb',
    'rust': '.rs',
    'scala': '.scala',
    'fortran': '.f90',
    'bash': '.sh',
    'apl': '.apl',
    'gerbil': '.ss',
    'julia': '.jl',
    'vb': '.vb',
    'dart': '.dart',
    'zig': '.zig',
    'swift': '.swift',
    'nim': '.nim',
}


def create_template(
        language: str,
        problemid: str,
        src_layout: bool = False) -> None:
    """Create a template file for the specified language and problem ID.

    Args:
        language (str): The programming language (e.g., 'python3', 'cpp').
        problemid (str): The problem ID, used for the filename.
        src_layout (bool): If True, create a src/ directory structure.
    """
    language = language.lower()
    home_templates = os.path.expanduser('~/kattis_templates')

    def _check_kattis_templates() -> bool:
        # Always use ~/kattis_templates as the user-facing template directory
        # On first use, if not present, copy all default templates from
        # package data
        if not os.path.isdir(home_templates):
            try:
                # Use importlib.resources to access kattis_templates as a
                # package resource
                src = pkg_resources.files("kattis_cli") / "kattis_templates"
                shutil.copytree(str(src), home_templates)
            except Exception as e:
                console.print(
                    f"[bold red]❌  Could not \
copy templates: [/bold red] {e} ")
                return False
        return True

    def _get_main_template(language: str) -> str:
        main_templates = Path(home_templates).joinpath('main')
        for file in main_templates.iterdir():
            # print(file.stem.lower(), language)
            if file.is_file() and file.stem.lower() == language:
                return str(file)
        return ''

    console = Console()
    if not _check_kattis_templates():
        console.print(
            f"[bold red]❌ Templates '{language}' \
not found in [/bold red] {home_templates}! ")
        return

    def _copytree_with_problemid(src: str,
                                 dst: str,
                                 problemid: str) -> None:
        for root, _, files in os.walk(src):
            rel = os.path.relpath(root, src)
            target_root = os.path.join(dst, rel) if rel != '.' else dst
            os.makedirs(target_root, exist_ok=True)
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(
                    target_root, f.replace('problemid', problemid))
                if os.path.exists(dst_file):
                    console.print(
                        f"[bold yellow]⚠️  File \
'{dst_file}' exists. Skipping copy. [/bold yellow]")
                else:
                    shutil.copy2(src_file, dst_file)

    # If src_layout, copy the project structure for the language
    if src_layout:
        proj_struct_root = Path(home_templates).joinpath('project_structure')
        lang_src_struct = proj_struct_root.joinpath(language)
        if os.path.isdir(lang_src_struct):
            _copytree_with_problemid(
                str(lang_src_struct), os.getcwd(), problemid)
            console.print(
                f"[bold green]✅ Created project \
structure for {language}. [/bold green]")
        target_dir = os.path.join("src")
    else:
        target_dir = "."

    main_template = _get_main_template(language=language)
    extension = LANGUAGE_EXTENSIONS.get(language, None)

    try:
        with open(str(main_template), 'r', encoding='utf-8') as tf:
            template_content = tf.read()
    except OSError:
        console.print(
            f"[bold red] ❌ Could not read \
template file: {main_template} [/bold red]")
        return

    if not main_template:
        return
    # Handle Java class naming convention (capitalize first letter)
    if language == 'java':
        class_name = problemid[0].upper(
        ) + problemid[1:] if problemid else "Main"
        filename = f"{class_name}{extension}"
        content = template_content.replace("{class_name}", class_name)
    else:
        filename = f"{problemid}{extension}"
        content = template_content

    dest_path = os.path.join(target_dir, filename)

    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        console.print(
            f"[bold yellow]⚠️  File '{dest_path}' exists \
with content. Skipping. [/bold yellow]")
        return

    try:
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        console.print(
            f"[bold green]✅ Created template \
'{dest_path}' for {language}.[/bold green]")
    except OSError as e:
        console.print(
            f"[bold red]❌ Failed to create template \
'{dest_path}': {e} [/bold red]")
