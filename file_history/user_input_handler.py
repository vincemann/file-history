import threading

from file_history.logging_config import configure_logger


class UserInputHandler:

    def __init__(self, app, options):
        self.logger = configure_logger(self.__class__.__name__)
        self.options = options
        self.app = app
        # this stuff is related to on_file_selected being called multiple times, see below
        self.file_selected = False
        self.lock = threading.Lock()

    # this method may be called twice on selection in specific cases
    # make sure this does not affect the program
    # todo fix this in the future
    def on_file_selected(self, selected):
        with self.lock:
            if self.file_selected:
                return
            self.file_selected = True
            self.app.on_file_selected(selected)
