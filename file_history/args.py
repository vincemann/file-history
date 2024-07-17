from file_history.action import Action
from file_history.interface_mode import InterfaceMode

SCRIPT_NAME = "file-history.py"

# default values
DEFAULT_MODE = InterfaceMode.TERMINAL
DEFAULT_ACTION = Action.EDIT
DEFAULT_MAX_RESULTS = 35
DEFAULT_MAX_SCANNED_FILES = -1
DEFAULT_EDITOR = 'nano'

# args
MAX_SCANNED_FILES_ARG = "--max-scanned"
MAX_RESULT_FILES_ARG = "--results"
ACTION_ARG = "--action"
FILTER_ARG = "--filter"
MODE_ARG = "--mode"

# env vars
HISTORY_FILE_ENV = "FILE_HIST_FILE"
MAX_RESULTS_ENV = "FILE_HIST_RESULTS"
MAX_SCANNED_ENV = "FILE_HIST_MAX_SCANNED"
MODE_ENV = "FILE_HIST_MODE"
EDITOR_ENV = "FILE_HIST_EDITOR"
