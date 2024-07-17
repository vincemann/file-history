import unittest
from file_history.file_path_resolver import FilePathResolver


class TestFilePathResolver(unittest.TestCase):

    def test_no_parent_directory(self):
        recent_dirs = ["/some/path/lol", "/dessen/path"]
        file = "filename"
        expected_dirs = ["/some/path/lol", "/dessen/path"]
        result_file, result_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, file)
        self.assertEqual(result_file, "filename")
        self.assertEqual(result_dirs, expected_dirs)

    def test_with_parent_directory(self):
        recent_dirs = ["/some/path/lol", "/dessen/path"]
        file = "../filename"
        expected_dirs = ["/some/path", "/dessen"]
        result_file, result_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, file)
        self.assertEqual(result_file, "filename")
        self.assertEqual(result_dirs, expected_dirs)

    def test_complex_parent_directory(self):
        recent_dirs = ["/some/path/lol", "/dessen/path"]
        file = "../../filename"
        expected_dirs = ["/some", "/"]
        result_file, result_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, file)
        self.assertEqual(result_file, "filename")
        self.assertEqual(result_dirs, expected_dirs)

    def test_remove_some_parent_directories(self):
        # too many ../ so one recent dir is excluded from further matching
        recent_dirs = ["/some/path/lol", "/dessen/path"]
        file = "../../../filename"
        expected_dirs = ["/"]
        result_file, result_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, file)
        self.assertEqual(result_file, "filename")
        self.assertEqual(result_dirs, expected_dirs)

    def test_remove_all_parent_directories(self):
        # too many ../ so no recent is left for further matching
        recent_dirs = ["/some/path/lol", "/dessen/path"]
        file = "../../../../filename"
        expected_dirs = []
        result_file, result_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, file)
        self.assertEqual(result_file, "filename")
        self.assertEqual(result_dirs, expected_dirs)

    def test_file_with_parent_directory(self):
        recent_dirs = ["/some/path/lol", "/dessen/path"]
        file = "/path/to/../dir/file.txt"
        expected_dirs = ["/some/path/lol", "/dessen/path"]
        result_file, result_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, file)
        self.assertEqual(result_file, "/path/dir/file.txt")
        self.assertEqual(result_dirs, expected_dirs)


if __name__ == "__main__":
    unittest.main()
