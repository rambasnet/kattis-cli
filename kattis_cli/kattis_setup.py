"""Setup file for Kattis.
"""

from pathlib import Path
import requests
from rich.console import Console
from rich.prompt import Prompt, Confirm
from . import kattis
from .utils import config


_LOGIN_URL = 'https://open.kattis.com/login'
_KATTISRCURL = "https://open.kattis.com/download/kattisrc"
_HEADERS = {'User-Agent': 'kattis-cli'}
_KATTISRC = Path.home().joinpath(".kattisrc")


def check_kattisrc() -> bool:
    """Check if kattisrc exists.

    Returns:
        bool: True if kattisrc exists, False otherwise.
    """
    try:
        cfg = config.get_kattisrc()
        response = kattis.login_from_config(cfg)
        if response.status_code != 200:
            return False
    except config.ConfigError:
        return False
    return True


def setup() -> None:
    """Setup Kattis CLI.
    """
    console = Console()
    console.print(":cat: Welcome to Kattis CLI! :cat:", style="bold blue")
    if check_kattisrc():
        console.print(
            ":rocket: [bold blue]kattisrc already exists with valid token.[/]")
        console.print(
            ":rocket: [bold green]You are ready to use Kattis CLI.[/]")
        return
    console.print("You need your Kattis credentials for this setup.")
    if Confirm.ask("Do you have an account on Kattis?", default=True):
        while True:
            username = Prompt.ask(
                "Please enter your username or email",
                password=False,
            )
            while True:
                password = Prompt.ask(
                    "Please enter your password",
                    password=True,
                )
                if Confirm.ask("Want to see your password? ", default=False):
                    console.print(f"You entered: {password}")
                    if Confirm.ask("Is this correct? ", default=True):
                        console.print(":rocket: Logging in...")
                        break
                else:
                    console.print(":rocket: Logging in...")
                    break

            response = kattis.login(_LOGIN_URL, username, password)
            if response.status_code == 200:
                console.print(":rocket: Login successful!")
                # download kattisrc
                cookies = response.cookies
                # print(cookies)
                res = requests.get(
                    _KATTISRCURL,
                    cookies=cookies,
                    headers=_HEADERS,
                    timeout=5,
                )
                if res.status_code == 200:
                    with open(_KATTISRC, "w", encoding='utf-8') as f:
                        f.write(res.text)
                    console.print(f""":rocket: kattisrc
downloaded and saved to {str(_KATTISRC)}""")
                else:
                    text = """:loudly_crying_face:
kattisrc download failed. "Please download kattisrc manually from:
[link=https://open.kattis.com/download/kattisrc]
https://open.kattis.com/download/kattisrc[/link]
and save it to your home directory with the name .kattisrc
"""
                    console.print(text)
                break
            else:
                console.print(""":loudly_crying_face:
Login failed. Please try again.""")
    else:
        console.print("Please register your account at: ")
        console.print("""[link="https://open.kattis.com/register"]
https://open.kattis.com/register[/link]""")
        console.print("and try again.")
