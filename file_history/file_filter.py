import re

from file_history.file_checker import FileChecker
from file_history.logging_config import configure_logger


class FileFilter:

    def __init__(self, filter):
        self.logger = configure_logger(self.__class__.__name__)
        self.files_read = []
        self.filter = filter
        self.filter_active = filter is not None and filter.strip() is not None
        self.file_checker = FileChecker()

    def accept(self, file):
        self.logger.debug("checking file: %s" % file)
        if self.already_seen(file):
            self.logger.debug("file already seen: %s" % file)
            return False
        self.files_read.append(file)
        if self.filter_active and self.is_ignored_by_filter(file):
            return False
        if not self.is_existing_file(file):
            self.logger.debug("file is not an existing directory: %s" % file)
            return False
        return True

    def already_seen(self, file):
        return file in self.files_read

    def is_ignored_by_filter(self, file):
        return not re.search(self.filter, file)

    def is_existing_file(self, file):
        return self.file_checker.isfile(file)


