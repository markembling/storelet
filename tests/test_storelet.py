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
        """Make sure the __enter__ method returns the instance"""
        b = storelet.ZipBackup("test")
        self.assertIs(b.__enter__(), b)

    def test_creates_and_removes_temporary_file(self):
        """Check the temporary file is created and removed"""
        with storelet.ZipBackup("test") as b:
            self.assertTrue(os.path.exists(b._path))
        self.assertFalse(os.path.exists(b._path))

    def test_close_removes_temporary_file(self):
        """
        Close method should remove temporary file 
        (in case the context manager isn't used)
        """
        b = storelet.ZipBackup("test")
        b.close()
        self.assertFalse(os.path.exists(b._path))

    def test_temporary_file_is_zipfile(self):
        """Make sure the file is in fact a ZIP"""
        with storelet.ZipBackup("test") as b:
            zipfile.is_zipfile(b._path)

    def test_sets_backup_name(self):
        with storelet.ZipBackup("test") as b:
            self.assertEqual(b.name, "test")

    def test_include_directory_simple(self):
        """
        Ensure a simple directory's contents are added to the backup
        """
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"))

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            self.assertIn("file.txt", names)

    def test_include_directory_recurse(self):
        """
        Ensure a full directory including subdirectory contents is added 
        to the backup
        """
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("deeper"))

            zip_file = zipfile.ZipFile(b._path, "r")
            names = zip_file.namelist()
            self.assertIn("file.txt", names)
            self.assertIn("dir1/file.txt", names)


if __name__ == '__main__':
    unittest.main()
