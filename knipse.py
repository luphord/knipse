#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''knipse - CLI catalog manager for pix and gThumb
'''

__author__ = '''luphord'''
__email__ = '''luphord@protonmail.com'''
__version__ = '''0.1.1'''


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

mycmd_parser = subparsers.add_parser('mycmd', help='An example subcommand')
mycmd_parser.add_argument('-n', '--number',
                          help='some number',
                          default=17, type=int)


def _mycmd(args: Namespace) -> None:
    print('Running mycmd subcommand with n={}...'.format(args.number))
    print('mycmd completed')


mycmd_parser.set_defaults(func=_mycmd)


def main() -> None:
    args = parser.parse_args()
    if args.version:
        print('''knipse ''' + __version__)
    elif hasattr(args, 'func'):
        args.func(args)


if __name__ == '__main__':
    main()
