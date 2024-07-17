import unittest
from unittest.mock import MagicMock, patch

from file_history.file_filter import FileFilter


class TestFileFilter(unittest.TestCase):

    def setUp(self):
        self.mock_file_checker = MagicMock()
        patch('file_history.file_filter.FileChecker', return_value=self.mock_file_checker).start()
        self.addCleanup(patch.stopall)

    def files_exist(self, files):
        def mock_isfile(path):
            return path in files
        self.mock_file_checker.isfile.side_effect = mock_isfile

    def test_reject_non_existing_file(self):
        # given
        file_filter = FileFilter("")
        self.mock_file_checker.isfile.return_value = False

        # when
        result = file_filter.accept("/home/user/nonexisting")

        # then
        self.assertFalse(result)

    def test_reject_empty_file(self):
        # given
        file_filter = FileFilter("")
        self.mock_file_checker.isfile.return_value = False

        # when
        result = file_filter.accept("")

        # then
        self.assertFalse(result)

    def test_reject_duplicate_file(self):
        # given
        file_filter = FileFilter("")
        self.mock_file_checker.isfile.return_value = True

        # when
        result1 = file_filter.accept("/home/user/documents")
        result2 = file_filter.accept("/home/user/documents")

        # then
        self.assertTrue(result1)
        self.assertFalse(result2)

    def test_filter_files(self):
        # given
        filter_pattern = "foo|bar"
        file_filter = FileFilter(filter_pattern)
        self.mock_file_checker.isfile.return_value = True

        # when
        result1 = file_filter.accept("/home/user/foo")
        result2 = file_filter.accept("/home/user/bar")
        result3 = file_filter.accept("/home/user/other")

        # then
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertFalse(result3)


if __name__ == '__main__':
    unittest.main()
