"""Copy config file to home directory.
"""

import shutil
import os
from pathlib import Path

config_file = Path.home().joinpath(".kattis-cli.toml")
# find current script path
script_path = Path(os.path.realpath(__file__)).parent
src_file = script_path.joinpath(".kattis-cli.toml")

if not config_file.exists():
    shutil.copy(src_file, config_file)
    # print(f"Config file {config_file} created.")
