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
        yield Path(f.get('uri').replace('file://', '')).resolve()


class Catalog:
    def __init__(self, files):
        self.files = list(files)

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


def main() -> None:
    args = parser.parse_args()
    if args.version:
        print('''knipse ''' + __version__)
    elif hasattr(args, 'func'):
        args.func(args)


if __name__ == '__main__':
    main()
