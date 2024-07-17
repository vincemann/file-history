import io
import os
import sys
import textwrap
import unittest
from unittest.mock import patch

from file_history.args import HISTORY_FILE_ENV, SCRIPT_NAME
from file_history.track.track_app import USAGE_STRING, TrackApp
from test.integration.suite.utils import assert_printed_to_stream, resolve_test_file_path


class TestTrackIntegration(unittest.TestCase):

    def setUp(self):
        self.file_history_path = resolve_test_file_path("file_history")
        self.default_env = os.environ.copy()
        self.stdout_buf = io.StringIO()

    def assert_printed_to_stdout(self, expected_outputs, strict=True):
        return assert_printed_to_stream(self.stdout_buf, expected_outputs, strict=strict)

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

    def start(self, dir, cmd):
        original_stdout = sys.stdout
        try:
            cli_args = [
                SCRIPT_NAME,
                "track",
            ]
            if dir:
                cli_args.append(dir)
            if cmd:
                cli_args.append(cmd)
            sys.argv = cli_args
            sys.stdout = self.stdout_buf
            TrackApp().start()
        finally:
            sys.stdout = original_stdout

    def read_file_history(self):
        with open(self.file_history_path, 'r') as f:
            return f.read().splitlines()

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_rel_file(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = "cat valid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_rel_file_with_dir_ending_with_slash(self, mock_isfile):
        # given
        dir = "/home/user/"
        cmd = "cat valid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_rel_files_from_cmd_chain(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = "cat valid_file4; nano valid_file5"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"
        expected_file_to_add_2 = "/home/user/valid_file5"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
            expected_file_to_add_2,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
            expected_file_to_add_2,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_rel_file_from_sub_shell_cmd(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = "bash -c \"cat valid_file4\""

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_dont_track_non_existing_rel_file(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = "cat valid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
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
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_existing_rel_file_and_dont_track_non_existing_rel_file(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = "cat valid_file4; touch invalid_file"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_abs_file(self, mock_isfile):
        # given
        dir = "/home/other"
        cmd = "cat /home/user/valid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_abs_and_rel_file(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = "cat /home/other/valid_file4 > target_file"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/other/valid_file4"
        expected_file_to_add_2 = "/home/user/target_file"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
            expected_file_to_add_2,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
            expected_file_to_add_2,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_duplicated_file(self, mock_isfile):
        # its clean's job to remove duplicates after
        # given
        dir = "/home/user"
        cmd = "cat valid_file1"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
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
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            "/home/user/valid_file1",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_dont_track_white_space_cmd(self, mock_isfile):
        # given
        dir = "/home/user"
        cmd = " "

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
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
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_track_abs_file_with_white_space_dir(self, mock_isfile):
        # given
        dir = " "
        cmd = "touch /home/user/valid_file4"
        expected_file_to_add = "/home/user/valid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            expected_file_to_add,
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_dont_track_white_space_cmd_and_whitespace_dir(self, mock_isfile):
        # given
        dir = " "
        cmd = " "

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
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
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.file_checker.FileChecker.isfile')
    def test_dont_track_non_existing_abs_file(self, mock_isfile):
        # given
        dir = "/home/other"
        cmd = "cat /home/user/invalid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()
        expected_file_to_add = "/home/user/valid_file4"

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)

    @patch('file_history.track.track_app.TrackApp.exit')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_no_cmd_given(self, mock_isfile, mock_exit):
        # given
        dir = "/home/other"
        cmd = None

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
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
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)
        mock_exit.assert_called_once_with(1)
        self.assert_printed_to_stdout(["Invalid amount of args, " + USAGE_STRING])

    @patch('file_history.track.track_app.TrackApp.exit')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_no_dir_given(self, mock_isfile, mock_exit):
        # given
        dir = None
        cmd = "cat /home/user/valid_file4"

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            "/home/user/valid_file4",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)
        mock_exit.assert_called_once_with(1)
        self.assert_printed_to_stdout(["Invalid amount of args, " + USAGE_STRING])

    @patch('file_history.track.track_app.TrackApp.exit')
    @patch('file_history.file_checker.FileChecker.isfile')
    def test_no_cmd_and_no_dir_given(self, mock_isfile, mock_exit):
        # given
        dir = None
        cmd = None

        file_history = textwrap.dedent("""
        /home/user/valid_file1
        /home/user/valid_file2
        /home/user/valid_file3\n
        """).strip()

        existing_files = [
            self.file_history_path,
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
            "/home/user/valid_file4",
        ]

        mock_isfile.side_effect = self.create_file_checker_mock(existing_files)
        self.setup_file_history(file_history)

        # when
        self.start(dir, cmd)

        # then
        expected_content = [
            "/home/user/valid_file1",
            "/home/user/valid_file2",
            "/home/user/valid_file3",
        ]
        actual_content = self.read_file_history()
        self.assertEqual(expected_content, actual_content)
        mock_exit.assert_called_once_with(1)
        self.assert_printed_to_stdout(["Invalid amount of args, " + USAGE_STRING])


if __name__ == '__main__':
    unittest.main()
