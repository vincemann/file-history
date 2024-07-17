class PathUtils:

    # example:
    # input: /path/to/dir & n = 1
    # return /path/to
    # may return with or without trailing '/'
    # only supports abs paths and n >= 0
    @staticmethod
    def reduce_paths(paths, n):
        reduced_paths = []
        if n < 0:
            raise Exception("n must be >= 0")
        if n == 0:
            return paths
        for path in paths:
            if path == '/' and n > 0:
                continue
            path_components = path.strip('/').split('/')

            # Remove the last n components
            if len(path_components) >= n:
                reduced_path = '/' + '/'.join(path_components[:-n])
                if reduced_path.strip():
                    reduced_paths.append(reduced_path)

        return reduced_paths

