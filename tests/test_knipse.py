import unittest
from pathlib import Path

from knipse import Catalog, parser, MissingFilesException


example_catalog = '''<?xml version="1.0" encoding="UTF-8"?>
<catalog version="1.0">
  <order inverse="0" type="general::unsorted"/>
  <files>
    <file uri="file:///path/to/file2.jpg"/>
    <file uri="file:///path/to/file3.jpg"/>
    <file uri="file:///path/to/file1.jpg"/>
  </files>
</catalog>
'''


class Testknipse(unittest.TestCase):

    def test_argument_parsing(self):
        args = parser.parse_args([])
        self.assertEqual(args.version, False)
        args = parser.parse_args(['--version'])
        self.assertEqual(args.version, True)

    def test_loading_catalog(self):
        catalog = Catalog.load_from_string(example_catalog)
        self.assertEqual(3, len(catalog.files))
        self.assertEqual('file2.jpg', catalog.files[0].name)
        self.assertEqual('file3.jpg', catalog.files[1].name)
        self.assertEqual('file1.jpg', catalog.files[2].name)

    def test_checking_catalog(self):
        catalog = Catalog([])
        catalog.check()  # empty catalog, noting missing
        catalog = Catalog([Path('/does/not/exist/873eghfsgdifsidhfksjdhf')])
        self.assertRaises(MissingFilesException, catalog.check)
