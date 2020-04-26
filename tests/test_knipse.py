import unittest
from pathlib import Path
import shutil
import tempfile

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


def create_example_image(image_path):
    image_path.parent.mkdir(exist_ok=True, parents=True)
    with open(image_path, 'wb') as f:
        f.write(b'\x00')
    return image_path


def create_example_images_iter(base_path):
    '''Create a folder structure with example images in a generator.'''
    images_path = base_path / 'images'
    yield create_example_image(images_path / 'p1.png')
    yield create_example_image(images_path / 'p2.png')
    yield create_example_image(images_path / 'folder1' / 'p3.png')
    yield create_example_image(images_path / 'folder1' / 'p4.png')
    yield create_example_image(images_path / 'folder2' / 'p5.png')
    yield create_example_image(images_path / 'folder2' / 'subfldr' / 'p6.png')


def create_example_images(base_path):
    '''Create a folder structure with example images.'''
    return list(create_example_images_iter(base_path))


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

    def test_example_images(self):
        tmp = Path(tempfile.mkdtemp())
        create_example_images(tmp)
        shutil.rmtree(tmp)
