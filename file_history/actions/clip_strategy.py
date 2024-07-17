import sys

import pyperclip

from file_history.actions.file_action_strategy import FileActionStrategy
from file_history.logging_config import configure_logger


class ClipStrategy(FileActionStrategy):

    def __init__(self, options):
        self.options = options
        self.logger = configure_logger(self.__class__.__name__)

    def perform(self, file: str) -> None:
        self.logger.debug("copy file to clipboard")
        if file is None:
            print("nothing selected", file=sys.stderr)
            return
        pyperclip.copy(file)
