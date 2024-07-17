import sys

from file_history.error_msgs import FILE_HISTORY_FILE_NOT_FOUND_MSG
from file_history.file_checker import FileChecker
from file_history.logging_config import configure_logger


class FileHistoryManager:

    def __init__(self, file_history_path):
        self.logger = configure_logger(self.__class__.__name__)
        self.file_history_path = file_history_path
        self.file_checker = FileChecker()

    def create_if_missing(self):
        file = self.file_history_path
        if not self.file_checker.isfile(file):
            print(FILE_HISTORY_FILE_NOT_FOUND_MSG(file), file=sys.stderr)
            self.create_file_history_file(file)

    def create_file_history_file(self, path):
        try:
            with open(path, 'w'):
                pass
            self.logger.debug(f"file_history file at: {path} has been created.")
        except Exception as e:
            self.logger.error("could not create file_history file at %s" % path)
            raise e
