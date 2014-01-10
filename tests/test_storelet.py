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

    def test_include_directory_preserving_paths(self):
        """
        Ensure full paths are preserved if the preserve_paths option is
        True
        """
        self.assertFalse(True, "TODO")

    def test_include_directory_with_name(self):
        """
        Ensure directory contents are added to a named directory if a 
        name is given
        """
        self.assertFalse(True, "TODO")

    def test_include_directory_with_name_and_paths(self):
        """
        Ensure a named directory is created with the full path preserved
        underneath it within the backup if both options are given
        """
        self.assertFalse(True, "TODO")

    def test_include_directory_merges_same_names(self):
        """
        Ensure that if two directories are included using the same name,
        both sets of files are included within the appropriate directory
        """
        self.assertFalse(True, "TODO")

    def test_resulting_file_is_zipfile(self):
        """
        Make sure the file is in fact a ZIP after adding some contents
        """
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"))
            zipfile.is_zipfile(b._path)

    def test_include_new_dir(self):
        """
        Check that we can create a new custom directory in the backup
        """
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
