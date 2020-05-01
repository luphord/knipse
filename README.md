# knipse

[![PyPI package](https://img.shields.io/pypi/v/knipse)](https://pypi.python.org/pypi/knipse)
[![Build status](https://img.shields.io/travis/luphord/knipse)](https://travis-ci.org/luphord/knipse)

CLI catalog manager for pix and gThumb

## Features
* `knipse` is a single file Python project

## Install

You can install `knipse` using `pip` with

```bash
pip3 install knipse
```

or you can simply download `knipse.py` and then run it using `python3` with

```bash
python3 knipse.py
```

## History

### 0.3.0 (2020-05-01)
* `check` subcommand for checking existence of files in catalog
* `check` subcommand walks folder structure and checks each catalog found if no catalog is specified
* drop support for Python 3.5
* `Catalog` instances can be serialized to xml
* `Catalog` instances can be iterated and compared for equality

### 0.2.0 (2020-03-22)
* Catalog class for parsing catalog xml files
* `ls` subcommand for listing files in catalog

### 0.1.1 (2020-03-21)
* fix linter error

### 0.1.0 (2020-03-21)
* Created using [cookiecutter-pyscript](https://github.com/luphord/cookiecutter-pyscript)

## Credits

Main developer is luphord <luphord@protonmail.com>. [cookiecutter-pyscript](https://github.com/luphord/cookiecutter-pyscript) is used as project template.
