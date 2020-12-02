import unittest
from pathlib import Path
import shutil
import tempfile

from knipse import Catalog, parser, MissingFilesException, iterate_catalogs


example_catalog = """<?xml version="1.0" encoding="UTF-8"?>
<catalog version="1.0">
  <order inverse="0" type="general::unsorted"/>
  <files>
    <file uri="file:///path/to/file2.jpg"/>
    <file uri="file:///path/to/file3.jpg"/>
    <file uri="file:///path/to/file1.jpg"/>
  </files>
</catalog>
"""


def create_example_image(image_path):
    image_path.parent.mkdir(exist_ok=True, parents=True)
    with open(image_path, "wb") as f:
        f.write(b"\x00")
    return image_path


def create_example_images_iter(base_path):
    """Create a folder structure with example images in a generator."""
    images_path = base_path / "images"
    yield create_example_image(images_path / "p1.png")
    yield create_example_image(images_path / "p2.png")
    yield create_example_image(images_path / "folder1" / "p3.png")
    yield create_example_image(images_path / "folder1" / "p4.png")
    yield create_example_image(images_path / "folder2" / "p5.png")
    yield create_example_image(images_path / "folder2" / "subfldr" / "p6.png")


def create_example_images(base_path):
    """Create a folder structure with example images."""
    return list(create_example_images_iter(base_path))


def create_example_catalog(catalog_path, images):
    catalog_path.parent.mkdir(exist_ok=True, parents=True)
    Catalog(images).write(catalog_path)
    return catalog_path


def create_example_catalogs(base_path, images):
    """Create a folder structure with example catalogs."""
    images = list(images)
    catalogs_path = base_path / "catalogs"
    img1 = images[2:]
    yield create_example_catalog(catalogs_path / "c1.catalog", img1), img1
    img2 = list(reversed(images[3:]))
    yield create_example_catalog(catalogs_path / "c2.catalog", img2), img2
    img3 = images[-3:]
    path3 = catalogs_path / "somelibrary" / "c3.catalog"
    yield create_example_catalog(path3, img3), img3


def create_example_images_and_catalogs(base_path):
    """Create a folder structure with example images and catalogs."""
    images = create_example_images(base_path)
    yield from create_example_catalogs(base_path, images)


class Testknipse(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog.load_from_string(example_catalog)

    def test_argument_parsing(self):
        args = parser.parse_args([])
        self.assertEqual(args.version, False)
        args = parser.parse_args(["--version"])
        self.assertEqual(args.version, True)

    def test_loading_catalog(self):
        self.assertEqual(3, len(self.catalog.files))
        self.assertEqual("file2.jpg", self.catalog.files[0].name)
        self.assertEqual("file3.jpg", self.catalog.files[1].name)
        self.assertEqual("file1.jpg", self.catalog.files[2].name)

    def test_loading_paths_with_spaces(self):
        p = Path("/path/to file with spaces")
        catalog1 = Catalog([p])
        self.assertEqual(p, catalog1.files[0])
        catalog2 = Catalog.load_from_xml(catalog1.to_xml())
        self.assertEqual(p, catalog2.files[0])
        self.assertEqual(catalog1, catalog2)

    def test_comparing_catalog(self):
        catalog1 = Catalog.load_from_string(example_catalog)
        catalog2 = Catalog.load_from_string(example_catalog)
        catalog3 = Catalog(catalog1.files)
        self.assertEqual(catalog1, catalog2)
        self.assertEqual(catalog1, catalog3)
        del catalog3.files[-1]
        self.assertNotEqual(catalog1, catalog3)
        self.assertNotEqual(Catalog([]), catalog1)
        catalog2.files.reverse()
        self.assertNotEqual(catalog1, catalog2)
        catalog1.files.reverse()
        self.assertEqual(catalog1, catalog2)

    def test_iteration(self):
        a = set(self.catalog)
        b = set(self.catalog.files)
        self.assertEqual(a, b)

    def test_len(self):
        self.assertEqual(len(self.catalog), 3)

    def test_xml_serialization(self):
        catalog1 = Catalog.load_from_string(example_catalog)
        catalog2 = Catalog.load_from_xml(catalog1.to_xml())
        self.assertEqual(catalog1, catalog2)
        tmpdir = Path(tempfile.mkdtemp())
        catalog_path = tmpdir / "my.catalog"
        catalog1.write(catalog_path)
        catalog3 = Catalog.load_from_file(catalog_path)
        self.assertEqual(catalog1, catalog3)
        shutil.rmtree(tmpdir)

    def test_checking_catalog(self):
        catalog = Catalog([])
        catalog.check()  # empty catalog, noting missing
        tmp = Path(tempfile.mkdtemp())
        all_images = create_example_images(tmp)
        catalog1 = Catalog(all_images)
        catalog2 = Catalog(all_images[1:])
        all_images[0].unlink()  # delete first image (contained in catalog1)
        self.assertRaises(MissingFilesException, catalog1.check)
        catalog2.check()
        shutil.rmtree(tmp)  # delete all remaining images
        self.assertRaises(MissingFilesException, catalog2.check)

    def test_walking_catalogs_folder_structure(self):
        tmp = Path(tempfile.mkdtemp())
        catalogs_images = list(create_example_images_and_catalogs(tmp))
        existing_catalogs = dict(iterate_catalogs(tmp))
        for catalog_path, images in catalogs_images:
            self.assertTrue(catalog_path.exists())
            for image in images:
                self.assertTrue(image.exists())
            catalog = existing_catalogs.pop(catalog_path)
            self.assertEqual(catalog, Catalog(images))
            catalog.check()
        shutil.rmtree(tmp)

    def test_skipping_empty_catalogs(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "empty.catalog").touch()
        self.assertFalse(list(iterate_catalogs(tmp)))

    def test_example_images(self):
        tmp = Path(tempfile.mkdtemp())
        create_example_images(tmp)
        shutil.rmtree(tmp)

    def test_symlinking(self):
        tmp = Path(tempfile.mkdtemp())
        catalog = Catalog(create_example_images(tmp))
        tmp2 = Path(tempfile.mkdtemp()) / "subdir"
        catalog.create_symlinks(tmp2)
        for fname in catalog:
            self.assertTrue((tmp2 / fname.name).exists())
        self.assertRaises(FileExistsError, lambda: catalog.create_symlinks(tmp2))
        catalog.create_symlinks(tmp2, force_override=True)
        shutil.rmtree(tmp)
        shutil.rmtree(tmp2)

    def test_symlinking_with_index(self):
        tmp2 = Path(tempfile.mkdtemp()) / "subdir"
        self.catalog.create_symlinks(tmp2, index_prefix=True)
        # cannot use Path.exists() as the link targets do not exist
        self.assertTrue((tmp2 / "0_file2.jpg").is_symlink())
        self.assertTrue((tmp2 / "1_file3.jpg").is_symlink())
        self.assertTrue((tmp2 / "2_file1.jpg").is_symlink())
        shutil.rmtree(tmp2)
