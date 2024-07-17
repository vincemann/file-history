import os


from file_history.args import HISTORY_FILE_ENV
from file_history.clean.file_history_cleaner import FileHistoryCleaner
from file_history.env_var_file_validator import get_file_from_env_var


class CleanApp:

    def exit(self, code):
        exit(code)

    def start(self):
        try:
            file = get_file_from_env_var(HISTORY_FILE_ENV)
            cleaner = FileHistoryCleaner(file)
            cleaner.clean()
        except Exception as e:
            print(e)
            self.exit(1)




