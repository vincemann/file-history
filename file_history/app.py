import threading
from abc import ABC, abstractmethod

from file_history.actions.file_action_stragey_provider import provide_file_action_strategy
from file_history.file_checker import FileChecker
from file_history.file_history_manager import FileHistoryManager
from file_history.logging_config import configure_logger


class App(ABC):

    def __init__(self, options, delay_start=False):
        self.logger = configure_logger(self.__class__.__name__)
        self.file_checker = FileChecker()
        self.options = options
        self.reader = None
        self.start_event = threading.Event()
        self.init_start_event(delay_start)
        self.search = None
        self.user_quit = False

    @abstractmethod
    def run(self):
        pass

    def init_start_event(self, delay_start):
        if not delay_start:
            self.start_event.set()

    def get_reader(self):
        return self.search.reader

    def signal_start(self):
        self.start_event.set()

    def close_program(self):
        if self.search:
            self.search.end()

    def on_file_selected(self, file):
        print(file)
        action = provide_file_action_strategy(self.options)
        if action:
            action.perform(file)
        self.close_program()

    def create_file_history_file_if_missing(self):
        FileHistoryManager(self.options.file_history).create_if_missing()

    def wait_for_start_event(self):
        self.start_event.wait()

    def is_search_started(self):
        return self.search.is_started()

    def is_search_done(self):
        return self.search.is_done()

    def end_search(self):
        self.search.end()

    def stream_cd_history(self):
        self.reader.read()
