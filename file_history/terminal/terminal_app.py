import sys

from file_history.app import App
from file_history.error_msgs import *
from file_history.logging_config import configure_logger
from file_history.search import Search
from file_history.terminal.terminal_popup import TerminalPopup
from file_history.terminal.terminal_userinput_handler import TerminalUserInputHandler
from file_history.terminal.terminal_ui import TerminalUi


class TerminalApp(App):

    def __init__(self, options, delay_start=False):
        super().__init__(options, delay_start=delay_start)
        self.logger = configure_logger(self.__class__.__name__)
        self.ui = self.create_ui()
        self.popup = TerminalPopup(self.ui, options)
        self.user_input_handler = TerminalUserInputHandler(self, options)

    def create_ui(self):
        if self.options.action == Action.SHOW:
            # files need to be printed to stdout and without numbers to allow interprocess communication like:
            # file-history --action=show | grep foo
            return TerminalUi(print_file_stream=sys.stdout, print_numbers=False)
        else:
            # print result files to stderr
            # set stream explicitly here and not using defaults, bc streams are replaced with buffers in my tests
            # for asserting what is printed to stdout/err
            return TerminalUi(print_file_stream=sys.stderr, print_numbers=True)

    def user_quits_program(self):
        self.user_quit = True
        self.close_program()

    def close_program(self):
        super().close_program()
        if self.options.action is not Action.SHOW:
            self.ui.stop_selection()

    def show_file(self, file):
        self.ui.show_file(file)

    def let_user_select_file(self):
        # blocking call
        self.ui.select_file(
            cancel_callback=self.user_input_handler.on_cancel_terminal_input,
            select_file_callback=self.user_input_handler.on_file_selected
        )

    def on_end_search(self):
        # quit_by_user should not be true if he just stopped the search
        if self.user_quit or len(self.search.files_read) == 0:
            # wait here to prevent race condition, that ends up with forever open stdin
            self.ui.wait_until_selection_started()
            self.ui.stop_selection()

    def run(self):
        self.create_file_history_file_if_missing()
        # needs to be done here
        self.search = Search(self.options,
                             file_found_callback=self.show_file,
                             end_search_callback=self.on_end_search)
        self.wait_for_start_event()

        if self.options.popup:
            self.options.filter = self.popup.ask_for_filter()

        self.search.start()

        if self.options.action is not Action.SHOW:
            # wait for input
            self.let_user_select_file()
        self.search.join()
