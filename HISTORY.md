## History

### 0.8.0 (2022-11-20)
* Drop support for Python 3.6 and 3.7
* Add support for Python 3.9, 3.10 and 3.11
* Upgrade development dependencies

### 0.7.1 (2021-09-27)
* fix domain error when symlinking empty catalog
* prevent resolution errors in paths with symlinks

### 0.7.0 (2021-08-03)
* `symlink` can prefix links with their index via `-i/--index-prefix`
* support loading empty catalog files

### 0.6.0 (2020-11-25)
* `catalogs` subcommand for listing available catalogs
* `symlink` subcommand for creating symlinks to files in catalog; also supports directory structure
* migrate to travis-ci.com
* use black for formatting
* `ls` iterates all available catalogs if none are given as argument

### 0.5.0 skipped by mistake

### 0.4.1 (2020-05-03)
* print help when no subcommand is given

### 0.4.0 (2020-05-03)
* `create` subcommand for creating catalogs by reading image file names from stdin
* fix loading image paths containing spaces

### 0.3.2 (2020-05-01)
* upgrade `twine` in order to have working checks with markdow readme + history

### 0.3.1 (2020-05-01)
* set `long_description_content_type` to `text/markdown` for proper rendering on [PyPI](https://pypi.python.org/pypi/knipse)

### 0.3.0 (2020-05-01)
* `check` subcommand for checking existence of files in catalog
* `check` subcommand walks folder structure and checks each catalog found if no catalog is specified
* drop support for Python 3.5
* `Catalog` instances can be serialized to xml
* `Catalog` instances can be iterated and compared for equality

### 0.2.0 (2020-03-22)
* `Catalog` class for parsing catalog xml files
* `ls` subcommand for listing files in catalog

### 0.1.1 (2020-03-21)
* fix linter error

### 0.1.0 (2020-03-21)
* Created using [cookiecutter-pyscript](https://github.com/luphord/cookiecutter-pyscript)
