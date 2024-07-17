import threading

from file_history.exception_thread import ExceptionThread
from file_history.file_checker import FileChecker
from file_history.file_filter import FileFilter
from file_history.file_history_reader import FileHistoryReader
from file_history.logging_config import configure_logger


class Search:

    def __init__(self, options, file_found_callback, end_search_callback):
        self.logger = configure_logger(self.__class__.__name__)
        self.options = options
        self.search_thread = ExceptionThread(target=self.run)
        self.file_found_callback = file_found_callback
        self.end_search_callback = end_search_callback
        self.files_read = []
        self.reader = self.create_reader()
        self.file_checker = FileChecker()
        self.started = False
        self.filter = None

    def create_reader(self):
        return FileHistoryReader(self.options.file_history,
                                 self.options.max_scanned,
                                 callback=self.on_file_found)

    def is_started(self):
        return self.started

    def is_done(self):
        if not self.is_started():
            return False
        else:
            return not self.search_thread.is_alive()

    def join(self):
        self.search_thread.join()

    def start(self):
        # needs to be done here bc of some timing issues
        # -> options.filter can change but this constructor needs to be called early
        self.filter = FileFilter(self.options.filter)
        self.logger.debug("starting search thread")
        self.search_thread.start()
        self.started = True

    # this code is executed on thread starting
    def run(self):
        self.reader.read()
        self.end_search_callback()

    def end(self):
        if self.is_done():
            # already ended
            return
        self.logger.debug("ending search")
        self.reader.stop()

    def on_file_found(self, file):
        if not self.filter.accept(file):
            return
        if self.read_enough_files():
            self.end()
        else:
            self.file_found_callback(file)
        self.files_read.append(file)

    def read_enough_files(self):
        files_left_to_find = self.options.max_results - len(self.files_read)
        return files_left_to_find <= 0

