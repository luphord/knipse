#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""knipse - CLI catalog manager for pix and gThumb
"""

__author__ = """luphord"""
__email__ = """luphord@protonmail.com"""
__version__ = """0.8.0"""


import sys
import os
import urllib
import math
import shutil
import hashlib
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from pathlib import Path
from xml.etree import ElementTree


base_catalog = """<?xml version="1.0" encoding="UTF-8"?>
<catalog version="1.0">
  <order inverse="0" type="general::unsorted"/>
  <files>
  </files>
</catalog>
"""


def _iter_files(xml):
    for f in xml.find("files").findall("file"):
        fname = urllib.parse.unquote(f.get("uri").replace("file://", ""))
        yield Path(fname)


class MissingFilesException(Exception):
    def __init__(self, missing_files):
        self.missing_files = missing_files

    def __str__(self):
        mfs = ", ".join(str(mf) for mf in self.missing_files)
        return "missing {}".format(mfs)


class Catalog:
    def __init__(self, files):
        self.files = list(files)

    def _update(self, sources, destination):
        assert destination
        for i, f in enumerate(self.files):
            for source in sources:
                replaced = None
                if f == source:
                    if destination.is_dir():
                        replaced = destination / f.name
                    else:
                        replaced = destination
                elif source in f.parents:
                    replaced = destination / f.relative_to(source)
                if replaced:
                    self.files[i] = replaced
                    yield f, replaced

    def update(self, sources, destination):
        """Update file paths that are affected by a move of any element
        in sources to destination.
        """
        return list(self._update(sources, destination))

    def missing_files(self):
        """Yield all files in catalog that do not exist on the file system."""
        for file_path in self:
            if not file_path.exists():
                yield file_path

    def __eq__(self, other):
        if not isinstance(other, Catalog):
            return False
        if len(self.files) != len(other.files):
            return False
        return all(f1 == f2 for (f1, f2) in zip(self, other))

    def __iter__(self):
        for file_path in self.files:
            yield file_path

    def __len__(self):
        return len(self.files)

    def check(self):
        missing = list(self.missing_files())
        if missing:
            raise (MissingFilesException(missing))

    def to_xml(self):
        xml = ElementTree.fromstring(base_catalog)
        files_xml = xml.find("files")
        for file_path in self:
            file_element = ElementTree.SubElement(files_xml, "file")
            file_element.attrib["uri"] = file_path.as_uri()
        return ElementTree.ElementTree(xml)

    def create_symlinks(self, directory, force_override=False, index_prefix=False):
        """Create symlinks to all files in catalog in `directory`"""
        ndigits = math.ceil(math.log10(len(self) or 1))
        index_fmt = "{:0" + str(ndigits) + "d}_{}"
        for i, file_path in enumerate(self):
            os.makedirs(directory, exist_ok=True)
            fname = (
                index_fmt.format(i, file_path.name) if index_prefix else file_path.name
            )
            link_path = directory / fname
            if force_override and link_path.exists():
                link_path.unlink()
            os.symlink(file_path.absolute(), link_path)

    def write(self, file):
        self.to_xml().write(file, encoding="utf8", short_empty_elements=True)

    def image_hashes(self):
        """Return sha1 hashes of all existing images
        (image content, not name) in catalog"""
        for file_path in self:
            if file_path.exists():
                yield file_path, hashlib.sha1(file_path.read_bytes())

    @staticmethod
    def load_from_xml(xml):
        return Catalog(_iter_files(xml))

    @staticmethod
    def load_from_file(fname):
        if Path(fname).stat().st_size == 0:
            # pix creates empty catalog files initially, i.e. xml is invalid
            # and loading it needs to be handled as a special case
            return Catalog([])
        xml = ElementTree.parse(fname)
        return Catalog.load_from_xml(xml)

    @staticmethod
    def load_from_string(s):
        xml = ElementTree.fromstring(s)
        return Catalog.load_from_xml(xml)


def iterate_catalogs(base_path):
    """Walk directories below `base_path` and yield all catalogs."""
    for root, dirs, files in os.walk(base_path):
        for file_path in files:
            file_path = Path(root, file_path)
            if file_path.suffix == ".catalog":
                yield file_path, Catalog.load_from_file(file_path)


parser = ArgumentParser(
    description="CLI catalog manager for pix and gThumb",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--version", help="Print version number", default=False, action="store_true"
)
parser.add_argument(
    "-p",
    "--catalogs-base-path",
    type=Path,
    help="Base path containing libraries and catalogs",
    default=Path.home() / ".local/share/pix/catalogs",
)

subparsers = parser.add_subparsers(
    title="subcommands", dest="subcommand", help="Available subcommands"
)

# ls subcommand

ls_parser = subparsers.add_parser("ls", help="List files of a catalog")
ls_parser.add_argument("catalog", type=Path, nargs="*")


def _ls(args: Namespace) -> None:
    for catalog_path, catalog in _load_catalogs(args.catalog, args.catalogs_base_path):
        for file_path in catalog.files:
            print(file_path)


ls_parser.set_defaults(func=_ls)

# check subcommand

check_parser = subparsers.add_parser(
    "check",
    help="Check existence of images in catalog",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
check_parser.add_argument("catalog", type=Path, nargs="*")


def _load_catalogs(args_catalog, catalogs_base_path):
    if args_catalog:
        for catalog_path in args_catalog:
            yield catalog_path, Catalog.load_from_file(catalog_path)
    else:
        yield from iterate_catalogs(catalogs_base_path)


def _check(args: Namespace) -> None:
    missing = []
    for catalog_path, catalog in _load_catalogs(args.catalog, args.catalogs_base_path):
        catalog = Catalog.load_from_file(catalog_path)
        try:
            catalog.check()
        except MissingFilesException as e:
            missing.append("{} {}".format(catalog_path, str(e)))
    if missing:
        raise Exception("Missing files in catalogs:\n" + "\n".join(missing))


check_parser.set_defaults(func=_check)

# symlink subcommand

symlink_parser = subparsers.add_parser(
    "symlink", help="Create symlinks to all files in catalog"
)
symlink_parser.add_argument(
    "-o",
    "--output-directory",
    type=Path,
    help="Directory where symlinks are to be created",
    default=Path.cwd(),
)
symlink_parser.add_argument(
    "-f",
    "--force-override",
    help="Override existing files",
    default=False,
    action="store_true",
)
symlink_parser.add_argument(
    "-i",
    "--index-prefix",
    help="Prefix the link file name with the image index, e.g. 123_fname.jpg",
    default=False,
    action="store_true",
)
symlink_parser.add_argument(
    "-d",
    "--directory-structure",
    help="Create a directory structure of symlinks for multiple catalogs",
    default=False,
    action="store_true",
)
symlink_parser.add_argument("catalog", type=Path, nargs="*")


def _symlink(args: Namespace) -> None:
    output_base = Path(args.output_directory)
    for catalog_path, catalog in _load_catalogs(args.catalog, args.catalogs_base_path):
        if args.directory_structure:
            output_path = output_base / Path(catalog_path).relative_to(
                args.catalogs_base_path
            ).with_suffix("")
        else:
            output_path = output_base
        catalog.create_symlinks(output_path, args.force_override, args.index_prefix)


symlink_parser.set_defaults(func=_symlink)

# mv subcommand

mv_parser = subparsers.add_parser(
    "mv",
    help="Move src to dest (similar to unix command mv) "
    "and update all references to src in catalogs",
)
mv_parser.add_argument("src", type=Path, nargs="+")
mv_parser.add_argument("dest", type=Path, nargs=1)


def _move(args: Namespace) -> None:
    assert len(args.dest) == 1
    dest = args.dest[0].resolve()
    if dest.exists() and not dest.is_dir():
        raise FileExistsError(dest)
    if len(args.src) > 1:
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
    for source in args.src:
        shutil.move(str(source), str(dest))
    for catalog_path, catalog in _load_catalogs(None, args.catalogs_base_path):
        updates = catalog.update(args.src, dest)
        if updates:
            catalog.write(catalog_path)
            print(catalog_path)
            for s, d in updates:
                print(f"    {s} -> {d}")


mv_parser.set_defaults(func=_move)

# create subcommand

create_parser = subparsers.add_parser(
    "create", help="Create a catalog by reading file names from stdin"
)


def _paths_from_stdin():
    for line in sys.stdin.readlines():
        line = line.strip()
        if line:
            yield Path(line).resolve()


def _create(args: Namespace) -> None:
    catalog = Catalog(_paths_from_stdin())
    catalog.write(sys.stdout.buffer)


create_parser.set_defaults(func=_create)

# catalogs subcommand

catalogs_parser = subparsers.add_parser("catalogs", help="List available catalogs")


def _catalogs(args: Namespace) -> None:
    for path, catalog in iterate_catalogs(args.catalogs_base_path):
        print(path)


catalogs_parser.set_defaults(func=_catalogs)


def main() -> None:
    args = parser.parse_args()
    if args.version:
        print("""knipse """ + __version__)
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
