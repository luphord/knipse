#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''knipse - CLI catalog manager for pix and gThumb
'''

__author__ = '''luphord'''
__email__ = '''luphord@protonmail.com'''
__version__ = '''0.2.0'''


from argparse import ArgumentParser, Namespace
from pathlib import Path
from xml.etree import ElementTree


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
        for file_path in self.files:
            if not file_path.exists():
                yield file_path

    def __eq__(self, other):
        if not isinstance(other, Catalog):
            return False
        if len(self.files) != len(other.files):
            return False
        return all(f1 == f2 for (f1, f2) in zip(self.files, other.files))

    def check(self):
        missing = list(self.missing_files())
        if missing:
            raise(MissingFilesException(missing))

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


parser = ArgumentParser(description='CLI catalog manager for pix and gThumb')
parser.add_argument('--version',
                    help='Print version number',
                    default=False,
                    action='store_true')

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


check_parser = subparsers.add_parser('check', help='Check existence of '
                                                   'images in catalog')
check_parser.add_argument('catalog', type=Path, nargs='+')


def _check(args: Namespace) -> None:
    missing = []
    for catalog_path in args.catalog:
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
