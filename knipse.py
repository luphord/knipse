#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''knipse - CLI catalog manager for pix and gThumb
'''

__author__ = '''luphord'''
__email__ = '''luphord@protonmail.com'''
__version__ = '''0.3.0'''


import os
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from pathlib import Path
from xml.etree import ElementTree


base_catalog = '''<?xml version="1.0" encoding="UTF-8"?>
<catalog version="1.0">
  <order inverse="0" type="general::unsorted"/>
  <files>
  </files>
</catalog>
'''


def _iter_files(xml):
    for f in xml.find('files').findall('file'):
        yield Path(f.get('uri').replace('file://', ''))


class MissingFilesException(Exception):
    def __init__(self, missing_files):
        self.missing_files = missing_files

    def __str__(self):
        mfs = ', '.join(str(mf) for mf in self.missing_files)
        return 'missing {}'.format(mfs)


class Catalog:
    def __init__(self, files):
        self.files = list(files)

    def missing_files(self):
        '''Yield all files in catalog that do not exist on the file system.'''
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

    def check(self):
        missing = list(self.missing_files())
        if missing:
            raise(MissingFilesException(missing))

    def to_xml(self):
        xml = ElementTree.fromstring(base_catalog)
        files_xml = xml.find('files')
        for file_path in self:
            file_element = ElementTree.SubElement(files_xml, 'file')
            file_element.attrib['uri'] = file_path.as_uri()
        return ElementTree.ElementTree(xml)

    def write(self, file):
        self.to_xml().write(file, encoding='utf8', short_empty_elements=True)

    @staticmethod
    def load_from_xml(xml):
        return Catalog(_iter_files(xml))

    @staticmethod
    def load_from_file(fname):
        xml = ElementTree.parse(fname)
        return Catalog.load_from_xml(xml)

    @staticmethod
    def load_from_string(s):
        xml = ElementTree.fromstring(s)
        return Catalog.load_from_xml(xml)


def iterate_catalogs(base_path):
    '''Walk directories below `base_path` and yield all catalogs.'''
    for root, dirs, files in os.walk(base_path):
        for file_path in files:
            file_path = Path(root, file_path).resolve()
            if file_path.suffix == '.catalog':
                yield file_path, Catalog.load_from_file(file_path)


parser = ArgumentParser(description='CLI catalog manager for pix and gThumb',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('--version',
                    help='Print version number',
                    default=False,
                    action='store_true')
parser.add_argument('-p', '--catalogs-base-path',
                    type=Path,
                    help='Base path containing libraries and catalogs',
                    default=Path.home() / '.local/share/pix/catalogs')

subparsers = parser.add_subparsers(title='subcommands', dest='subcommand',
                                   help='Available subcommands')

ls_parser = subparsers.add_parser('ls', help='List files of a catalog')
ls_parser.add_argument('catalog', type=Path, nargs='+')


def _ls(args: Namespace) -> None:
    for catalog_path in args.catalog:
        catalog = Catalog.load_from_file(catalog_path)
        for file_path in catalog.files:
            print(file_path)


ls_parser.set_defaults(func=_ls)


check_parser = \
    subparsers.add_parser('check',
                          help='Check existence of images in catalog',
                          formatter_class=ArgumentDefaultsHelpFormatter)
check_parser.add_argument('catalog', type=Path, nargs='*')


def _load_catalogs(args_catalog, catalogs_base_path):
    if args_catalog:
        for catalog_path in args_catalog:
            yield catalog_path, Catalog.load_from_file(catalog_path)
    else:
        yield from iterate_catalogs(catalogs_base_path)


def _check(args: Namespace) -> None:
    missing = []
    for catalog_path, catalog in _load_catalogs(args.catalog,
                                                args.catalogs_base_path):
        catalog = Catalog.load_from_file(catalog_path)
        try:
            catalog.check()
        except MissingFilesException as e:
            missing.append('{} {}'.format(catalog_path, str(e)))
    if missing:
        raise Exception('Missing files in catalogs:\n' + '\n'.join(missing))


check_parser.set_defaults(func=_check)


def main() -> None:
    args = parser.parse_args()
    if args.version:
        print('''knipse ''' + __version__)
    elif hasattr(args, 'func'):
        args.func(args)


if __name__ == '__main__':
    main()
