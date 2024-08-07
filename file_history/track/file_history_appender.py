import os

from file_history.logging_config import configure_logger


class FileHistoryAppender:

    def __init__(self, history_file):
        self.logger = configure_logger(self.__class__.__name__)
        self.history_file = history_file

    def append(self, line):
        self.logger.debug("adding line to file_history file: %s" % line)
        with open(self.history_file, 'a') as file:
            file.write(self.adjust_newlines(line))

    def is_file_empty(self):
        return os.stat(self.history_file).st_size == 0

    def file_ends_with_newline(self):
        with open(self.history_file, 'rb') as file:
            file.seek(-1, 2)  # Move the cursor to the last byte in the file
            last_char = file.read(1)
            return last_char == b'\n'

    # make sure file ends with newline, otherwise prepend newline
    # avoids /my/path/my/path2
    # instead:
    # /my/path
    # /my/path2
    def needs_prepending_newline(self):
        return not self.is_file_empty() and not self.file_ends_with_newline()

    def adjust_newlines(self, dir):
        # make sure ends with new line
        dir_line = dir.strip() + '\n'
        if self.needs_prepending_newline():
            dir_line = '\n' + dir_line
        return dir_line
