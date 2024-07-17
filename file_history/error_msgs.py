from file_history.args import *


MISSING_FILE_HISTORY_ENV_VAR_MSG = (f"{HISTORY_FILE_ENV} env var not set.")
def FILE_HISTORY_FILE_NOT_FOUND_MSG(location): return (f"Cant find file history file at: {location}. Generating.")
