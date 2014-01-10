import os
import unittest
import storelet

class TestZipBackup(unittest.TestCase):
    def test_context_manager_enter(self):
        b = storelet.ZipBackup("test")
        self.assertIs(b.__enter__(), b)

    def test_creates_and_removes_temporary_file(self):
        with storelet.ZipBackup("test") as b:
            self.assertTrue(os.path.exists(b._path))
        self.assertFalse(os.path.exists(b._path))

    def test_close_removes_temporary_file(self):
        b = storelet.ZipBackup("test")
        b.close()
        self.assertFalse(os.path.exists(b._path))

    def test_sets_backup_name(self):
        with storelet.ZipBackup("test") as b:
            self.assertEqual(b.name, "test")

if __name__ == '__main__':
    unittest.main()
