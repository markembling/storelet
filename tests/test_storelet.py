import os
import unittest
import zipfile
import logging
import storelet

class StoreletTestCase(unittest.TestCase):
    def get_data(self, name):
        """Gets the path to the named test data"""
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", name)

    @classmethod
    def setUpClass(cls):
        super(StoreletTestCase, cls).setUpClass()
        logger = logging.getLogger(storelet.__name__)
        cls._log_handler = MockLoggingHandler(level="DEBUG")
        logger.addHandler(cls._log_handler)
        cls.log_messages = cls._log_handler.messages

    def setUp(self):
        super(StoreletTestCase, self).setUp()
        self._log_handler.reset()

    def assertLogged(self, level, message):
        """
        Assert that a message was logged containing the given text and 
        at the given level
        """
        for logmsg in self.log_messages[level]:
            if message in logmsg:
                return
        raise AssertionError(
            "No %s log message containing '%s'" % (level, message))

class FakeBackup(object):

    """Fake backup object for checking methods were called"""

    def __init__(self):
        self.include_directory_called = False
        self.include_directory_name = None

    def include_directory(self, path, **kwargs):
        self.include_directory_called = True
        self.include_directory_name = kwargs["name"]

class MockLoggingHandler(logging.Handler):

    """
    Mock logging handler to check for expected logs

    Messages are available from an instance's ``messages`` dict, in 
    order, indexed by a lowercase log level string (e.g., 'debug', 
    'info', etc.)

    From: http://stackoverflow.com/a/20553331/6844
    """

    def __init__(self, *args, **kwargs):
        self.messages = {'debug': [], 
                         'info': [], 
                         'warning': [], 
                         'error': [],
                         'critical': []}
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        """
        Store a message from ``record`` in the instance's ``messages`` 
        dict.
        """
        self.acquire()
        try:
            self.messages[record.levelname.lower()].append(record.getMessage())
        finally:
            self.release()

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                # Empty the list
                del message_list[:]
        finally:
            self.release()


class TestZipBackup(StoreletTestCase):

    """Tests for the ZipBackup class"""

    def test_context_manager_enter(self):
        """__enter__ method should return instance"""
        b = storelet.ZipBackup("test")
        self.assertIs(b.__enter__(), b)
        b.close()

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
        """Name is correctly set"""
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

    def test_logging_when_creating_and_removing_file(self):
        """Log messages when creating and removing temporary file"""
        with storelet.ZipBackup("test") as b:
            pass
        self.assertLogged("debug", "Created temporary file")
        self.assertLogged("debug", "Removed temporary file")

    def test_logging_when_adding_directory(self):
        """Log messages when adding a directory"""
        with storelet.ZipBackup("test") as b:
            b.include_directory(self.get_data("simple"))
        self.assertLogged("debug", "Adding directory")
        self.assertLogged("debug", "Walking directory")
        self.assertLogged("info", "Added file")
        self.assertLogged("debug", "Finished directory")

class TestBackupIncludedDirectory(StoreletTestCase):

    """Tests for the BackupIncludedDirectory class"""

    def setUp(self):
        super(TestBackupIncludedDirectory, self).setUp()
        self.fake_backup = FakeBackup()

    def test_sets_name(self):
        """Name is correctly set"""
        with storelet.BackupIncludedDirectory("test", self.fake_backup) as d:
            self.assertEqual(d.name, "test")

    def test_creates_and_removes_temporary_directory(self):
        """Temporary directory is created and removed"""
        with storelet.BackupIncludedDirectory("test", self.fake_backup) as d:
            self.assertTrue(os.path.isdir(d.path))
        self.assertFalse(os.path.exists(d.path))

    def test_string_representation(self):
        """String representation is current temporary path on disk"""
        with storelet.BackupIncludedDirectory("test", self.fake_backup) as d:
            self.assertEqual(str(d), d.path)

    def test_context_manager_enter(self):
        """__enter__ method should return instance"""
        d = storelet.BackupIncludedDirectory("test", self.fake_backup)
        self.assertIs(d.__enter__(), d)
        d.__exit__(None, None, None)

    def test_included_in_owner_backup(self):
        """Directory is included in the backup with the given name"""
        with storelet.BackupIncludedDirectory("test", self.fake_backup) as d:
            pass
        self.assertTrue(self.fake_backup.include_directory_called)
        self.assertEqual(self.fake_backup.include_directory_name, 
                         "test")

    def test_logging(self):
        """Log messages when creating/removing temporary directory"""
        with storelet.BackupIncludedDirectory("test", self.fake_backup) as d:
            pass
        self.assertLogged("debug", "Created temporary directory")
        self.assertLogged("debug", "Removed temporary directory")


if __name__ == '__main__':
    unittest.main()
