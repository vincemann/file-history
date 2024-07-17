import unittest

from file_history.path_utils import PathUtils


class TestPathUtils(unittest.TestCase):

    def test_reduce_paths(self):
        test_cases = [
            (['/path/to/dir'], 1, ['/path/to']),
            (['/path/to/dir'], 0, ['/path/to/dir']),
            (['/path/to/dir/'], 0, ['/path/to/dir/']),
            (['/path/to/dir'], 2, ['/path']),
            (['/path/to/dir'], 3, ['/']),
            (['/path/to/dir'], 4, []),
            ([], 4, []),
            (['/path/to/dir/extra'], 2, ['/path/to']),
            (['/path/to/dir/extra'], 3, ['/path']),
            (['/path/to/dir/extra'], 4, ['/']),
            (['/path/to/dir/extra'], 5, []),
            (['/'], 1, []),
            (['/path/with/many/components/'], 2, ['/path/with']),
            (['/path/with/many/components/'], 4, ['/']),
            (['/path/with/many/components/'], 5, []),
            (['/path/with/many/components/'], 6, []),
            # multiple inputs
            (['/path/with/many/components/', '/some/other'], 1, ['/path/with/many', '/some']),
            (['/path/with/many/components/', '/some/other'], 3, ['/path']),
            (['/path/with/many/components/', '/some/other'], 5, []),
        ]

        for paths, n, expected in test_cases:
            with self.subTest(paths=paths, n=n):
                result = PathUtils.reduce_paths(paths, n)
                self.assertEqual(expected, result, "input: %d - %s" % (n, paths))


if __name__ == '__main__':
    unittest.main()
