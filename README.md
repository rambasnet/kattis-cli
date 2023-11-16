# Kattis-CLI

Kattis CLI - download, test and submit Kattis problems using CLI


## Installation

```bash
pip install kattis-cli
```

## Kattis configuration

- Create a file named `.kattisrc` in your home directory
- Login in to Kattis and download the `.kattisrc` file from the [Kattis settings page](https://open.kattis.com/download/kattisrc)


## Usage

```bash
kattis <command> [options]
```

### Commands

### Download a problem sample files and it's metadata

```bash
kattis get <problem_id>
```

### Display problem metadata

```bash
cd <problem_id>
kattis info
```

### Test a problem

```bash
cd <problem_id>
kattis test
```

### Submit a problem

```bash
cd <problem_id>
kattis submit
```
