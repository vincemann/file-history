from file_history.path_utils import PathUtils
import os


class FilePathResolver:

    @staticmethod
    def resolve_parent_directories(recent_dirs, file):
        # Normalize the file path to correctly handle '..'
        normalized_file = os.path.normpath(file)
        parent_dir_count = normalized_file.count("..")
        file = normalized_file.replace("../", "").replace("..", "")

        if parent_dir_count > 0:
            return file, PathUtils.reduce_paths(recent_dirs, parent_dir_count)
        else:
            return file, recent_dirs

    @staticmethod
    def resolve_home_directories(file):
        if file.startswith("~"):
            return os.getenv("HOME") + file[1:]
        else:
            return file

    @staticmethod
    def resolve_dot_slash_directories(file):
        if file.startswith("./"):
            return file[2:]
        else:
            return file
