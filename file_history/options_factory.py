import argparse
import os

from file_history.args import *
from file_history.options import Options


class OptionsFactory:

    def create(self):
        parser = argparse.ArgumentParser(description="Parse CLI arguments for file-history", prog="file-history")
        parser.add_argument(MODE_ARG, type=str, choices=[mode.value for mode in InterfaceMode],
                            help="Mode to display the last files")
        parser.add_argument(ACTION_ARG, type=str, choices=[action.value for action in Action],
                            help="Action to execute to the selected file")
        parser.add_argument(MAX_RESULT_FILES_ARG, type=int, help="Stop search after displaying this amount of matching files")
        parser.add_argument(FILTER_ARG, type=str, help="Filter regex or 'popup' for prompting user")
        parser.add_argument(MAX_SCANNED_FILES_ARG, type=int, help="Maximum number of files to search through (file_history)")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        args = parser.parse_args()

        mode = args.mode or os.getenv(MODE_ENV, DEFAULT_MODE)
        mode = InterfaceMode(mode)

        popup = args.filter == "popup"

        options = Options(
            mode=mode,
            action=args.action or DEFAULT_ACTION,
            max_results=args.results or int(os.getenv(MAX_RESULTS_ENV, DEFAULT_MAX_RESULTS)),
            filter=args.filter,
            max_scanned=args.max_scanned or int(os.getenv(MAX_SCANNED_ENV, DEFAULT_MAX_SCANNED_FILES)),
            editor=os.getenv(EDITOR_ENV, DEFAULT_EDITOR),
            file_history=os.getenv(HISTORY_FILE_ENV),
            popup=popup,
            debug=args.debug,
        )

        return options

