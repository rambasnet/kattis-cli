# Kattis-CLI

Kattis CLI - download, test and submit Kattis problems using CLI.
Based on Official Kattis CLI: [https://github.com/Kattis/kattis-cli](https://github.com/Kattis/kattis-cli)

## Requirements

- Python 3.6+
- [Kattis account](https://open.kattis.com/login/email)

## Windows

- Use Command Line or PowerShell
- Make sure python is in your PATH
- if you get codec error while running kattis-cli, run the following command in Command Prompt:

```bash
python --version
chcp 65001
```

```bash

## Installation

```bash
pip install kattis-cli
python -m pip install kattis-cli
```

## Kattis configuration

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

```bash
kattis get <problem_id>
```

![Get problem id from URL](images/get.png)

### Display problem metadata

```bash
cd <problem_id>
kattis info
```

![Problem info](images/info.png)

### Test a solution locally

- currently supported languages: Python 3, C++
- make sure python is in your PATH
- make sure python files have first line shebang: !/usr/bin/env python3
    - or have extensions .py3

```bash
cd <problem_id>
kattis test
```

![Test](images/test.png)

### Submit a problem

- see live results right on the terminal

```bash
cd <problem_id>
kattis submit
```

![Progress](images/progress.png)
![Result](images/result.png)
