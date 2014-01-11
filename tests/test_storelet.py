import os
import unittest
import zipfile
import storelet

class StoreletTestCase(unittest.TestCase):
    def get_data(self, name):
        """Gets the path to the named test data"""
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", name)

class TestZipBackup(StoreletTestCase):

    """Tests for the ZipBackup class"""

    def test_context_manager_enter(self):
        """__enter__ method should return instance"""
        b = storelet.ZipBackup("test")
        self.assertIs(b.__enter__(), b)

    def test_creates_and_removes_temporary_file(self):
        """Temporary file is created and removed"""
        with storelet.ZipBackup("test") as b:
            self.assertTrue(os.path.exists(b._path))
        self.assertFalse(os.path.exists(b._path))

    def test_close_removes_temporary_file(self):
        """Close method removes temporary file"""
        b = storelet.ZipBackup("test")
        b.close()
        self.assertFalse(os.path.exists(b._path))

    def test_sets_backup_name(self):
        with storelet.ZipBackup("test") as b:
            self.assertEqual(b.name, "test")

    def test_include_directory_simple(self):
        """A simple directory's contents are added"""
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"))

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            self.assertIn("file.txt", names)

    def test_include_directory_recurse(self):
        """Adds directory including subdirectory contents"""
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("deeper"))

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            self.assertIn("file0.txt", names)
            self.assertIn("dir1/file1.txt", names)

    def test_include_directory_preserving_paths(self):
        """Full paths are preserved if requested"""
        data_path = self.get_data("simple")
        with storelet.ZipBackup("test") as b:
            b.include_directory(data_path, preserve_paths=True)

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            # If the full path was '/dir1/dir2/file.txt', we want to 
            # make sure the zip file has an entry named 
            # 'dir1/dir2/file.txt' without the leading '/'.
            data_path_rootless = os.path.relpath(data_path, "/")
            self.assertIn("%s/file.txt" % data_path_rootless, names)

    def test_include_directory_with_name(self):
        """Directory contents are added to a named directory"""
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"), name="foo")

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            self.assertIn("foo/file.txt", names)

    def test_include_directory_with_name_and_paths(self):
        """A named directory is created with the full path preserved"""
        data_path = self.get_data("simple")
        with storelet.ZipBackup("test") as b:
            b.include_directory(data_path, preserve_paths=True, 
                                           name="foo")

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            data_path_rootless = os.path.relpath(data_path, "/")
            self.assertIn("foo/%s/file.txt" % data_path_rootless, names)

    def test_include_directory_merges_same_names(self):
        """
        Two directories' contents are merged into the same named 
        directory
        """
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"), name="foo")
            b.include_directory(self.get_data("deeper"), name="foo")

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            self.assertIn("foo/file.txt", names)
            self.assertIn("foo/file0.txt", names)
            self.assertIn("foo/dir1/file1.txt", names)

    def test_resulting_file_is_zipfile(self):
        """Make sure the file is a ZIP after adding some contents"""
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"))
            zipfile.is_zipfile(b._path)

    def test_include_new_dir(self):
        """A new custom directory can be added"""
        with storelet.ZipBackup("test") as b:
            with b.include_new_dir("new_dir") as d:
                # We need to write at least one file to the directory
                # as empty directories don't exist in zip files. The 
                # file heirarchy is just implied by the names of the 
                # members of the zip file.
                with open(os.path.join(str(d), "test.txt"), "w") as f:
                    f.write("Testing")

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()

            # If the name has the directory in it, the directory exists 
            # as far as the zip file and any archive tool is concerned.
            self.assertIn("new_dir/test.txt", names)

class TestBackupIncludedDirectory(StoreletTestCase):
    # TODO
    pass


if __name__ == '__main__':
    unittest.main()
