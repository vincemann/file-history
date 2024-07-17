import unittest
from file_history.command_parser import CommandParser
from unittest.mock import MagicMock
import os

BASH_HISTORY = '~/.bash_history'


class TestCommandParser(unittest.TestCase):

    def setUp(self):
        self.mock_file_checker = MagicMock()
        self.parser = CommandParser(self.mock_file_checker)
        self.default_env = os.environ.copy()

    def tearDown(self):
        os.environ = self.default_env

    def files_exist(self, files):
        def mock_isfile(path):
            return path in files
        self.mock_file_checker.isfile.side_effect = mock_isfile

    def test_abs_file(self):
        # given
        cmd = "ls /path/to/file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_program_only(self):
        # given
        cmd = "/bin/cat"
        self.files_exist(["/bin/cat"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_program_pipe_to_program(self):
        # given
        cmd = "/bin/cat | /bin/cat"
        self.files_exist(["/bin/cat"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_sub_shell_program_pipe_to_program(self):
        # given
        cmd = "bash -c '/bin/cat | /bin/cat'"
        self.files_exist(["/bin/cat"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_brackets_program(self):
        # given
        cmd = "[ -x /usr/bin/clear_console ]"
        self.files_exist(["/usr/bin/clear_console"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/usr/bin/clear_console"]
        self.assertEqual(expected_files, actual_files)

    def test_program_chain(self):
        # given
        cmd = "/bin/cat;/bin/cat"
        self.files_exist(["/bin/cat"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_program_in_subshell(self):
        # given
        cmd = "bash -c '/bin/cat'"
        self.files_exist(["/bin/cat"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_program_chain_in_subshell(self):
        # given
        cmd = "bash -c '/bin/cat;/bin/cat'"
        self.files_exist(["/bin/cat"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_only(self):
        # given
        cmd = "/path/foo"
        self.files_exist(["/path/foo"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_only(self):
        # given
        cmd = "foo"
        self.files_exist(["/path/foo"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_rel_program_only(self):
        # given
        cmd = "cat"
        self.files_exist(["/bin/cat"])
        recent_dirs = ["/bin"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_ignored_program_echo(self):
        # echo can never have a file arg
        # given
        cmd = "echo foo"
        self.files_exist(["/path/foo"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_echo_with_redirect(self):
        # echo can never have a file arg
        # given
        cmd = "echo \"foo\" > dessen"
        self.files_exist(["/path/dessen"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/dessen"]
        self.assertEqual(expected_files, actual_files)

    def test_echo_with_pipe(self):
        # echo can never have a file arg
        # given
        cmd = "echo \"foo\" | cat dessen"
        self.files_exist(["/path/dessen", "/path/foo"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/dessen"]
        self.assertEqual(expected_files, actual_files)

    def test_echo_with_pipe_cat_redirect(self):
        # echo can never have a file arg
        # given
        cmd = "echo \"foo\" | cat > dessen"
        self.files_exist(["/path/dessen", "/path/foo"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/dessen"]
        self.assertEqual(expected_files, actual_files)

    def test_echo_with_pipe_echo_redirect(self):
        # echo can never have a file arg
        # given
        cmd = "echo \"foo\" | echo > dessen"
        self.files_exist(["/path/dessen", "/path/foo"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/dessen"]
        self.assertEqual(expected_files, actual_files)

    def test_echo_with_double_redirect(self):
        # echo can never have a file arg
        # given
        cmd = "echo \"foo\" >> dessen"
        self.files_exist(["/path/dessen"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/dessen"]
        self.assertEqual(expected_files, actual_files)

    def test_subshell_with_echo_redirect(self):
        # echo can never have a file arg
        # given
        cmd = "bash -c 'echo \"foo\" > dessen'"
        self.files_exist(["/path/dessen"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/dessen"]
        self.assertEqual(expected_files, actual_files)

    def test_ignored_program_cd(self):
        # echo can never have a file arg
        # given
        cmd = "cd /path/foo"
        self.files_exist(["/path/foo"])
        recent_dirs = ["/path"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_program_with_args(self):
        # given
        cmd = "cat -n"
        self.files_exist(["/bin/cat", "/bin/n"])
        recent_dirs = ["/bin"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_with_newline(self):
        # given
        cmd = "ls /path/to/file.txt\n"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/some/other"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_spaces_only(self):
        # given
        cmd = "  "
        self.files_exist([])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_newline_only(self):
        # given
        cmd = "\n"
        self.files_exist([])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_subshell_single_quotes(self):
        # given
        cmd = "bash -c 'ls /path/to/file.txt'"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_subshell_chained(self):
        # given
        cmd = "bash -c 'ls /path/to/file.txt; cat foo | grep -i /abs/gil'"
        self.files_exist(["/path/to/file.txt", "/path/dessen/foo", "/abs/gil"])
        recent_dirs = ["/path/dessen"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt", "/path/dessen/foo", "/abs/gil"]
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_subshell_double_quotes(self):
        # given
        cmd = "bash -c \"ls /path/to/file.txt\""
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_subshell(self):
        # given
        cmd = "bash -c 'ls file.txt'"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_non_existing_abs_file(self):
        # given
        cmd = "ls /path/to/nonexistent/file.txt"
        self.files_exist([])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_non_existing_rel_file(self):
        # given
        cmd = "ls file2.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_with_double_quotes_and_spaces(self):
        # given
        cmd = "ls \"my file.txt\""
        self.files_exist(["/path/to/my file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/my file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_with_single_quotes_and_spaces(self):
        # given
        cmd = "ls 'my file.txt'"
        self.files_exist(["/path/to/my file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/my file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_with_single_quotes(self):
        # given
        cmd = "ls 'file.txt'"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_with_double_quotes(self):
        # given
        cmd = "ls \"file.txt\""
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_two_abs_files(self):
        # given
        cmd = "ls /path/to/file.txt > /path/to/other.txt"
        self.files_exist(["/path/to/file.txt", "/path/to/other.txt"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt", "/path/to/other.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_dot_slash(self):
        # given
        cmd = "ls ./file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_double_quotes_and_spaces(self):
        # given
        cmd = "ls \"my dessen file.txt\""
        self.files_exist(["/path/to/my dessen file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/my dessen file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_without_double_quotes_and_with_spaces(self):
        # given
        cmd = "ls my dessen file.txt"
        self.files_exist(["/path/to/my dessen file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_dot_dot_slash(self):
        # given
        cmd = "ls ../file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to/more"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_dot_dot_slash_ambiguous(self):
        # given
        cmd = "ls ../file.txt"
        self.files_exist(["/path/to/file.txt", "/path/to/more/file.txt"])
        recent_dirs = ["/path/to/more"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_multiple_dot_dot_slash(self):
        # given
        cmd = "ls ../../file.txt"
        self.files_exist(["/path/file.txt"])
        recent_dirs = ["/path/to/more"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_non_existent_abs_file(self):
        # given
        cmd = "ls /path/to/file.txt"
        self.files_exist([])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_no_recent_dirs(self):
        # given
        cmd = "ls /path/to/file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file(self):
        # given
        cmd = "ls file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_many_recent_dirs(self):
        # given
        cmd = "ls file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/other", "/path/dessen", "/dessen/path", "/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_tilde(self):
        # given
        cmd = "ls ~/file.txt"
        os.environ["HOME"] = "/home/gil"
        self.files_exist(["/home/gil/file.txt"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/home/gil/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_with_tilde_and_dotdot(self):
        # given
        cmd = "ls ~/../file.txt"
        os.environ["HOME"] = "/home/gil"
        self.files_exist(["/home/file.txt"])
        recent_dirs = []

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/home/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_not_in_recent_dirs(self):
        # given
        cmd = "ls file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/some/other"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = []
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_multiple_recent_dirs(self):
        # given
        cmd = "ls file.txt"
        self.files_exist(["/path/to/file.txt"])
        recent_dirs = ["/path/to", "/some/other"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_rel_file_double_match(self):
        # file.txt is in /path/to and /some/other and both dirs are recently visited
        # both should be added to result set
        # given
        cmd = "ls file.txt"
        self.files_exist(["/path/to/file.txt", "/some/other/file.txt"])
        recent_dirs = ["/path/to", "/some/other"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt", "/some/other/file.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_two_rel_files(self):
        # given
        cmd = "ls -la file.txt | grep dessen.txt"
        self.files_exist(["/path/to/file.txt", "/some/other/dessen.txt"])
        recent_dirs = ["/path/to", "/some/other"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt", "/some/other/dessen.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_one_rel_file_and_one_abs(self):
        # given
        cmd = "ls -la file.txt | grep /some/other/dessen.txt"
        self.files_exist(["/path/to/file.txt", "/some/other/dessen.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/path/to/file.txt", "/some/other/dessen.txt"]
        self.assertEqual(expected_files, actual_files)

    def test_abs_file_precedence_over_rel_file(self):
        # given
        cmd = "ls -la /some/other/file.txt"
        self.files_exist(["/some/other/file.txt", "/path/to/file.txt"])
        recent_dirs = ["/path/to"]

        # when
        actual_files = self.parser.find_files_in_command(cmd, recent_dirs)

        # then
        expected_files = ["/some/other/file.txt"]
        self.assertEqual(expected_files, actual_files)
