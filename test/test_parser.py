import unittest
from unittest.mock import MagicMock, Mock, call

from file_history.command_parser import CommandParser
from file_history.parser import Parser


class TestParserComponent(unittest.TestCase):

    def setUp(self):
        self.mock_file_checker = MagicMock()

    def files_exist(self, files):
        def mock_isfile(path):
            return path in files

        self.mock_file_checker.isfile.side_effect = mock_isfile

    def create_parser(self, recent_dirs, n=None):
        # Create a parser instance with the actual command parser implementation
        return Parser(
            recent_dirs,
            n,
            CommandParser(self.mock_file_checker)
        )

    def assert_callback_calls(self, mock_callback, expected_files_calls):
        calls = []
        for expected_files in expected_files_calls:
            calls.append(call(expected_files))
        self.assertEqual(len(calls), mock_callback.call_count)
        mock_callback.assert_has_calls(calls)

    def test_find_abs_files(self):
        # given
        bash_history = [
            "touch /some/path/file1",
            "echo 'hello' > /some/path/file2",
            "rm /some/path/file3"
        ]

        recent_dirs = [
            "/some/other/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/some/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        self.assert_callback_calls(mock_callback, [
            ["/some/path/file1"],
            ["/some/path/file2"],
            ["/some/path/file3"],
        ])

    def test_ignore_empty_lines(self):
        # given
        bash_history = [
            "",
            "echo 'hello' > /some/path/file2",
            "rm /some/path/file3"
        ]

        recent_dirs = [
            "/some/other/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/some/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        self.assert_callback_calls(mock_callback, [
            ["/some/path/file2"],
            ["/some/path/file3"],
        ])

    def test_ignore_duplicate_cmds(self):
        # file2 is not found twice and order indicates that it uses the most recent command
        # given
        bash_history = [
            "echo 'hello' > /some/path/file2",
            "cat /some/path/file1",
            "echo 'hello' > /some/path/file2",
            "ls /some/path/file3",
        ]

        recent_dirs = [
            "/some/other/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/some/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        self.assert_callback_calls(mock_callback, [
            ["/some/path/file2"],
            ["/some/path/file1"],
            ["/some/path/file3"],
        ])

    def test_find_n_files(self):
        # we have 3 files that could be found
        # but n is set to 2, so it stops after 2 files

        # given
        bash_history = [
            "touch /some/path/file1",
            "echo 'hello' > /some/path/file2",
            "rm /some/path/file3"
        ]

        recent_dirs = [
            "/some/other/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/some/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs, n=2)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        self.assert_callback_calls(mock_callback, [
            ["/some/path/file1"],
            ["/some/path/file2"],
        ])

    def test_find_n_files_overflow(self):
        # we have 3 files that could be found
        # but n is set to 2, so it stops after 2 files
        # one command has two files so we end up with either 1 or 3
        # it should be capped to 2

        # given
        bash_history = [
            "touch /some/path/file1",
            "echo 'hello' > /some/path/file2 /some/path/file3",
        ]

        recent_dirs = [
            "/some/other/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/some/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs, n=2)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1"],
            ["/some/path/file2"]
        ]

        self.assert_callback_calls(mock_callback, expected_files)

    def test_find_abs_files_no_recent_dirs(self):
        # given
        bash_history = [
            "touch /some/path/file1",
            "echo 'hello' > /some/path/file2",
            "rm /some/path/file3",
            "cat file4"
        ]

        recent_dirs = []

        existing_files = [
            "/some/path/file1",
            "/some/path/file2",
            "/some/path/file3",
            "/some/path/file4"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1"],
            ["/some/path/file2"],
            ["/some/path/file3"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_abs_file_duplicate_preserve_order_and_unique(self):
        # order needs to be preserved
        # /some/path/file1 should still be on top and not duplicated in result set
        # given
        bash_history = [
            "touch /some/path/file1",
            "echo 'hello' > /some/path/file2",
            "vim /some/path/file1"
        ]

        recent_dirs = []

        existing_files = [
            "/some/path/file1",
            "/some/path/file2"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1"],
            ["/some/path/file2"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_rel_file_duplicate_preserve_order_and_unique(self):
        # order needs to be preserved
        # /some/path/file1 should still be on top and not duplicated in result set
        # given
        bash_history = [
            "touch file1",
            "echo 'hello' > file2",
            "vim file1"
        ]

        recent_dirs = [
            "/some/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/some/path/file2"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1"],
            ["/some/path/file2"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_find_rel_files(self):
        # given
        bash_history = [
            "touch file1",
            "echo 'hello' > file2",
            "rm file3"
        ]

        recent_dirs = [
            "/some/path",
            "/some/other/path",
        ]

        existing_files = [
            "/some/path/file1",
            "/some/other/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1"],
            ["/some/other/path/file2"],
            ["/some/path/file3"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_multiple_rel_files_in_single_cmd(self):
        # look out for correct order

        # given
        bash_history = [
            "mv file1 file2",
            "echo 'hello' > file3",
            "sudo rm -rf /"
        ]

        recent_dirs = [
            "/some/path",
            "/some/other/path",
        ]

        existing_files = [
            "/some/path/file1",
            "/some/other/path/file2",
            "/some/path/file3"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1", "/some/other/path/file2"],
            ["/some/path/file3"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_mixed_rel_abs_and_non_existent_files(self):
        # file 1 exists
        # file 2 does not exist
        # file 3 does not exist in dir visited recently
        # file 4 exists

        # given
        bash_history = [
            "mv file1 file2",
            "echo 'hello' > file3",
            "sudo rm -rf /",
            "mv /dessen/file4 ../"
        ]

        recent_dirs = [
            "/some/path",
        ]

        existing_files = [
            "/some/path/file1",
            "/some/other/path/file3",
            "/dessen/file4"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/some/path/file1"],
            ["/dessen/file4"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_long_cmd_chain(self):
        # file 1 exists
        # file 2 does not exist
        # file 3 does not exist in dir visited recently
        # file 4 exists
        # given
        bash_history = [
            "sudo rm -rf /;mv /dessen/file4 ../ && cp file1",
        ]

        recent_dirs = [
            "/some/dir",
        ]

        existing_files = [
            "/some/dir/file1",
            "/dessen/file4",
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = [
            ["/dessen/file4", "/some/dir/file1"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_long_cmd_chain_filter(self):
        # file 1 exists
        # file 2 does not exist
        # file 3 does not exist in dir visited recently
        # file 4 exists
        # given
        bash_history = [
            "sudo rm -rf /;mv file4 ../ && cp file1; cat ./file3",
        ]

        recent_dirs = [
            "/dessen",
            "/some/deren",
            "/some/dessen",
        ]

        existing_files = [
            "/dessen/file4",
            "/some/deren/file1",
            "/some/dessen/file3",
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback, filter="dessen")

        # then
        expected_files = [
            ["/dessen/file4","/some/dessen/file3"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_find_rel_files_with_filter(self):
        # given
        bash_history = [
            "touch fileHello1",
            "echo 'hello' > fileHolla2",
            "rm file3Hello"
        ]

        recent_dirs = [
            "/some/path",
            "/some/other/path",
        ]

        existing_files = [
            "/some/path/fileHello1",
            "/some/other/path/fileHolla2",
            "/some/path/file3Hello"
        ]

        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback, filter="Hello")

        # then
        expected_files = [
            ["/some/path/fileHello1"],
            ["/some/path/file3Hello"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_find_rel_files_with_path_filter(self):
        # filter also applies to path
        # given
        bash_history = [
            "touch file1",
            "echo 'hello' > file2",
            "rm file3"
        ]

        recent_dirs = [
            "/some/path",
            "/some/other/path",
        ]

        existing_files = [
            "/some/path/file1",
            "/some/other/path/file2",
            "/some/path/file3"
        ]

        # when
        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback, filter="other")

        # then
        expected_files = [
            ["/some/other/path/file2"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_find_mixed_files_with_path_filter(self):
        # mix rel and absolute files, both match in path
        # given
        bash_history = [
            "touch /some/path/file1",
            "echo 'hello' > file2",
            "rm file3"
        ]

        recent_dirs = [
            "/some/path",
            "/dessen/path"
        ]

        existing_files = [
            "/some/path/file1",
            "/dessen/path/file2",
            "/some/path/file3"
        ]

        # when
        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback, filter="some")

        # then
        expected_files = [
            # abs
            ["/some/path/file1"],
            # rel
            ["/some/path/file3"]
        ]
        self.assert_callback_calls(mock_callback, expected_files)

    def test_find_no_files(self):
        # given
        bash_history = [
            "touch file1",
            "echo 'hello' > file2",
            "rm file3"
        ]

        recent_dirs = [
            "/some/path",
            "/some/other/path",
        ]

        existing_files = [
            "/somewhere/file1",
            "/somewhere/file2",
            "/somewhere/file3"
        ]

        # when
        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = []
        self.assert_callback_calls(mock_callback, expected_files)

    def test_non_existing_abs_files(self):
        # given
        bash_history = [
            "touch /path/to/file1",
            "echo 'hello' > /path/to/file2",
            "rm *"
        ]

        recent_dirs = []

        existing_files = [
            "/somewhere/file1",
            "/somewhere/file2",
            "/somewhere/file3"
        ]

        # when
        mock_callback = Mock()
        self.files_exist(existing_files)
        parser = self.create_parser(recent_dirs)

        # when
        parser.find_files(bash_history, mock_callback)

        # then
        expected_files = []
        self.assert_callback_calls(mock_callback, expected_files)


if __name__ == "__main__":
    unittest.main()
