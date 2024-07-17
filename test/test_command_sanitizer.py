import unittest
from file_history.command_sanitizer import CommandSanitizer


class TestCommandSanitizer(unittest.TestCase):

    def test_sudo_and_file(self):
        cmd_parts = ["sudo", "rm", "-rf", "/"]
        expected_result = ["/"]
        result = CommandSanitizer.remove_non_file_parts(cmd_parts)
        self.assertEqual(expected_result, result)

    def test_sudo_minus_i(self):
        cmd_parts = ["sudo", "-i"]
        expected_result = []
        result = CommandSanitizer.remove_non_file_parts(cmd_parts)
        self.assertEqual(expected_result, result)

    def test_bash_symbols(self):
        cmd_parts = ["echo", "hello", ">", "output.txt"]
        expected_result = ["hello", "output.txt"]
        result = CommandSanitizer.remove_non_file_parts(cmd_parts)
        self.assertEqual(expected_result, result)

    def test_only_command(self):
        cmd_parts = ["ls", "-la"]
        expected_result = []
        result = CommandSanitizer.remove_non_file_parts(cmd_parts)
        self.assertEqual(expected_result, result)

    def test_command_with_two_files(self):
        cmd_parts = ["mv", "/file1", "/file2"]
        expected_result = ["/file1", "/file2"]
        result = CommandSanitizer.remove_non_file_parts(cmd_parts)
        self.assertEqual(expected_result, result)

    def test_bash_symbols_only(self):
        cmd_parts = [">", "<<", ">>"]
        expected_result = []
        result = CommandSanitizer.remove_non_file_parts(cmd_parts)
        self.assertEqual(expected_result, result)


if __name__ == '__main__':
    unittest.main()
