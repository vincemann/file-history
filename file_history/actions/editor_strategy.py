import sys
import threading

from file_history.actions.file_action_strategy import FileActionStrategy
from file_history.editor import Editor
from file_history.logging_config import configure_logger
from file_history.track.file_history_appender import FileHistoryAppender


class EditorStrategy(FileActionStrategy):

    def __init__(self, options):
        self.logger = configure_logger(self.__class__.__name__)
        self.options = options

    def perform(self, file: str) -> None:
        if file is None:
            print("nothing selected", file=sys.stderr)
            return
        self.logger.debug("opening file in editor")
        self.append_file_to_history(file)
        editor = Editor(self.options.editor)
        threading.Thread(target=lambda: editor.open(file)).start()

    def append_file_to_history(self, file):
        appender = FileHistoryAppender(self.options.file_history)
        appender.append(file)

