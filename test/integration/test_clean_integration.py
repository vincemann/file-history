import os
import sys
import textwrap
import unittest
from unittest.mock import patch

from file_history.args import HISTORY_FILE_ENV, SCRIPT_NAME
from file_history.clean.clean_app import CleanApp

from test.integration.suite.utils import resolve_test_file_path


class TestCleanIntegration(unittest.TestCase):

    def setUp(self):
        self.file_history_path = resolve_test_file_path("file_history")
        self.default_env = os.environ.copy()

    def tearDown(self):
        os.environ = self.default_env

    def create_file_checker_mock(self, existing_files):
        def mock_isfile(path):
            return path in existing_files

        return mock_isfile

    def setup_file_history(self, content):
        path = self.file_history_path
        with open(path, 'w') as f:
            f.write(content)
        os.environ[HISTORY_FILE_ENV] = path
        return path

    def read_file_history(self):
        with open(self.file_history_path, 'r') as f:
            return f.read().splitlines()

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_remove_duplicate(self, mock_isfile):
        # given
        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3
        /home/user/valid_file2\n
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        CleanApp().start()

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file3",
            "/home/user/valid_file2",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_empty_file(self, mock_isfile):
        # given
        file_history = ""

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        CleanApp().start()

        # then
        expected_content = []
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_newline_file(self, mock_isfile):
        # given
        file_history = "\n"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        CleanApp().start()

        # then
        expected_content = []
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_all_valid(self, mock_isfile):
        # given
        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        CleanApp().start()

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3"
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_all_valid_with_whitespaces(self, mock_isfile):
        # given
        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid file2
        /home/user/valid_file3
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        CleanApp().start()

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid file2",
            "/home/user/valid_file3"
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_all_valid_multiple_iterations(self, mock_isfile):
        def assert_stayed_same():
            # then
            expected_content = [
                "/home/user/valid_file1",
                "/home/user/valid_file2",
                "/home/user/valid_file3"
            ]
            actual_content = self.read_file_history()
            self.assertEqual(expected_content, actual_content)
        # given
        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        for i in range(20):
            CleanApp().start()
            assert_stayed_same()

        assert_stayed_same()

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_fixes_then_stays_same_multiple_iterations(self, mock_isfile):
        def assert_correct_state():
            # then
            expected_content = [
                "/home/user/valid_file1",
                "/home/user/valid_file2",
                "/home/user/valid_file3",
            ]
            actual_content = self.read_file_history()
            self.assertEqual(expected_content, actual_content)
        # given
        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /some/unexisting
        /home/user/valid_file2
        invalid/file
        /home/user/valid_file3
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        for i in range(20):
            CleanApp().start()
            assert_correct_state()

        assert_correct_state()

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_clean_script_remove_non_existent_files(self, mock_isfile):
        # given
        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        cli_args = [
            SCRIPT_NAME,
            "clean",
        ]
        sys.argv = cli_args
        CleanApp().start()

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file3"
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)


if __name__ == '__main__':
    unittest.main()
