## History

### 0.5.0 (not yet)
* `catalogs` subcommand for listing available catalogs
* `symlink` subcommand for creating symlinks to files in catalog
* migrate to travis-ci.com

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
