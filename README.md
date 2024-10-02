# Kattis-CLI

Kattis CLI - download, test and submit Kattis problems using CLI.
Inspired by the official Kattis CLI: [https://github.com/Kattis/kattis-cli](https://github.com/Kattis/kattis-cli)

![Tests](https://github.com/rambasnet/kattis-cli/actions/workflows/ci-test.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/kattis-cli.svg)](https://badge.fury.io/py/kattis-cli)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/kattis-cli)](https://pypi.org/project/kattis-cli/)
[![PyPI - License](https://img.shields.io/pypi/l/kattis-cli)](https://pypi.org/project/kattis-cli/)

## Requirements

- Python 3.8+ (PyPy preferred as Kattis uses PyPy to run your Python3 solutions)
- [Kattis account](https://open.kattis.com/login/email)

## Windows

- Use Command Line or PowerShell
- Make sure python is in your PATH
    - Install Python from Windows Store
- if you get codec error while running kattis-cli, run the following command in Command Prompt:

```bash
python --version
chcp 65001
```

## Installation

If you've Python version 3.8 or higher, you can skip creating virtual environment. If you wish to create a virtual environment, see intructions below.


### Create and activate virtual environment using venv

- follow the instruction provided in the link to create and activate virtual environment:
[https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)


### Create and activate virtual environment using conda

- follow the instruction provided in the link to create and activate virtual environment:
[https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment)

## Install Kattis-cli

- activate virtual environment if you've created one for kattis-cli
- run the following command in Command Prompt or PowerShell

```bash
pip install kattis-cli
python -m pip install kattis-cli
kattis --version
```

- on Windows add the path shown in the output of the above command to your PATH environment variable

## Update/Upgrade Kattis-CLI

- remove or rename **.kattis-cli.toml** file in your home directory
- activate virtual environment if you've created one for kattis-cli

```bash
kattis --version
pip install kattis-cli --upgrade
python -m pip install kattis-cli --upgrade
```

- on Windows add the path shown in the output of the above command to your PATH environment variable


## Kattis configuration

- run the following command and enter your Kattis credentials
- this will create a .kattisrc file in your home directory

```bash
kattis setup
```

## Usage

```bash
kattis <command> [options]
kattis --help
```

### Commands

### Download a problem sample files and it's metadata

- problem id can be found in the last part of the URL of the problem
- example: [https://open.kattis.com/problems/cold](https://open.kattis.com/problems/cold) => problem id: **cold**

![Problem id](./images/problemid.png)

```bash
kattis get <problem_id>
```

![Get problem id from URL](./images/kattis_get.png)

### Display problem metadata

```bash
cd <problem_id>
kattis info
```

![Problem info](./images/kattis_info.png)

### Test a solution locally

![Test](images/kattis_test.png)

- currently the following languages have been tested: Python 3, C++, NodeJS, C, Java
- make sure CLI compilers are in your PATH
- make sure python3 files have first line shebang: !/usr/bin/env python3
    - or have extensions .py3
- update the **.kattis-cli.toml** file in your home directory to add more languages
- see [kattis_cli/.kattis-cli.toml](https://github.com/rambasnet/kattis-cli/blob/main/kattis_cli/.kattis-cli.toml) file for example.

```bash
cd <problem_id>
kattis test # for exact comparion of answers (string and int)
kattis test -a 6 # Answer accepted upto 6 decimal places of accuracy
```

### Testing floating point results

- for floating point ouput, problem provides the tolerance or accuracy upto certain decimal points
- one can use `-a <N>` switch after kattis test command to provide the decimal places of accuracy
- e.g., the following command checks for accuracy upto 6 decimal points or absolute error upto $10^-6$

```bash
kattis test -a 6
```


### Submit a problem

- make sure you've configured kattis-cli

```bash
kattis setup
```

- see live results right on the terminal

```bash
cd <problem_id>
kattis submit
```

![Result](images/kattis_verdict.png)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate. Adding support for more languages is highly appreciated.


## Using this Repo

- clone this repo
- create virtual environment with pypy 3.8 or higher
- using conda the following command creates kattis virtual environment with pypy3.8

### Using conda and virtual environment

```bash
conda create -c conda-forge -n kattis pypy python=3.8
conda activate kattis
```

- install dependencies

```bash
pip install -r requirements.txt
```

- run the following command to install kattis-cli from this repo on Mac/Linux

```bash
make
./build.sh
pip install dist/kattis_cli-x.x.x-py3-none-any.whl --force-reinstall  
```

### Using Docker

- clone this repo
- run the following command to build and run the Dockerfile provided in this repo
- if using Windows, run the following command in git-bash Terminal

```bash
bash run.sh
```
