import sys

from file_history.args import HISTORY_FILE_ENV
from file_history.command_parser import CommandParser
from file_history.dir_sanitizer import sanitize_dir
from file_history.env_var_file_validator import read_env_var
from file_history.file_checker import FileChecker
from file_history.file_history_manager import FileHistoryManager
from file_history.logging_config import configure_logger
from file_history.track.file_history_appender import FileHistoryAppender

USAGE_STRING = "usage: file-history track dir cmd"


class TrackApp:

    def __init__(self):
        self.logger = configure_logger(self.__class__.__name__)

    def get_cmd_arg(self):
        if len(sys.argv) != 4:
            raise Exception("Invalid amount of args, " + USAGE_STRING)
        cmd = sys.argv[3]
        return cmd

    def get_dir_arg(self):
        if len(sys.argv) != 4:
            raise Exception("Invalid amount of args, " + USAGE_STRING)
        cmd = sys.argv[2]
        return cmd

    def exit(self, code):
        exit(code)

    def get_file_history(self):
        path = read_env_var(HISTORY_FILE_ENV)
        FileHistoryManager(path).create_if_missing()
        return path

    def start(self):
        try:
            cmd = self.get_cmd_arg()
            curr_dir = self.get_dir_arg()
            curr_dir = sanitize_dir(curr_dir)
            history_file = self.get_file_history()
            cmd_parser = CommandParser(FileChecker())
            files = cmd_parser.find_files_in_command(cmd, [curr_dir])
            appender = FileHistoryAppender(history_file)
            for file in files:
                appender.append(file)
        except Exception as e:
            print(e)
            self.exit(1)
