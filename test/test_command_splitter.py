import unittest
from file_history.command_splitter import CommandSplitter


# only test stuff I added on top of shlex (subshell, delimiters), dont test shlex
class TestCommandSplitter(unittest.TestCase):

    def setUp(self):
        self.command_splitter = CommandSplitter()

    def test_simple_command(self):
        cmd = "ls -la /path/to/dir"
        expected = ["ls", "-la", "/path/to/dir"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_chained_cmd_with_comma(self):
        cmd = "sudo rm -rf /;mv /dessen/file4 ../"
        expected = [["sudo", "rm", "-rf", "/"], ["mv", "/dessen/file4", "../"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_cmd_with_trailing_comma(self):
        cmd = "sudo rm -rf /;"
        expected = ["sudo", "rm", "-rf", "/"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_chained_cmd_with_pipe(self):
        cmd = "sudo cat myfile | grep -i /dessen/file4"
        expected = [["sudo", "cat", "myfile"], ["grep", "-i", "/dessen/file4"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_chained_cmd_with_spaced_comma(self):
        cmd = "sudo rm -rf / ; mv /dessen/file4 ../"
        expected = [["sudo", "rm", "-rf", "/"], ["mv", "/dessen/file4", "../"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_chained_cmd_with_one_side_spaced_comma(self):
        cmd = "sudo rm -rf /; mv /dessen/file4 ../"
        expected = [["sudo", "rm", "-rf", "/"], ["mv", "/dessen/file4", "../"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_chained_cmd_with_commas(self):
        cmd = "sudo rm -rf /;mv /dessen/file4 ../;cat;echo gil"
        expected = [["sudo", "rm", "-rf", "/"], ["mv", "/dessen/file4", "../"], ["cat"], ["echo", "gil"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_command_with_quotes(self):
        cmd = 'echo "hello world"'
        expected = ["echo", "hello world"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_bash(self):
        cmd = "bash -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_with_commas(self):
        cmd = "bash -c 'ls /path/to/file; cat gil | grep foo'"
        expected = [["ls", "/path/to/file"], ["cat", "gil"], ["grep", "foo"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_double_subshell(self):
        cmd = "bash -c 'ls /path/to/file; bash -c \"ls gil; cat dessen | grep foo\"'"
        expected = [["ls", "/path/to/file"], [["ls", "gil"], ["cat", "dessen"], ["grep", "foo"]]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_zsh(self):
        cmd = "zsh -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_csh(self):
        cmd = "csh -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_tcsh(self):
        cmd = "tcsh -c 'ls /path/to/file'"
        expected = [ "ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_ksh(self):
        cmd = "ksh -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_dash(self):
        cmd = "dash -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_runuser(self):
        cmd = "runuser -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_subshell_command_sh(self):
        cmd = "sh -c 'ls /path/to/file'"
        expected = ["ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_complex_command(self):
        cmd = "bash -c 'echo \"nested quote\" && ls /path'"
        expected = [["echo", "nested quote"], ["ls", "/path"]]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_malformed_command(self):
        cmd = "bash -c 'ls /path/to/file"
        expected = []
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    # fair enough
    def test_invalid_subshell(self):
        cmd = "sh -c ls /path/to/file"
        expected = ["ls"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)

    def test_non_shell_minus_c(self):
        cmd = "other -c ls /path/to/file"
        expected = ["other", "-c", "ls", "/path/to/file"]
        result = self.command_splitter.split_command(cmd)
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()
