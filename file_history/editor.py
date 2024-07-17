import subprocess
import sys

from file_history.logging_config import configure_logger


class Editor:

    def __init__(self, editor):
        self.logger = configure_logger(self.__class__.__name__)
        self.editor = editor

    def open(self, file_path):
        # Construct the command to open the file
        command = [self.editor, file_path]

        # Run the command
        try:
            process = subprocess.Popen(command, stdin=None, stdout=None, stderr=None)
            process.wait()
            return process
        except subprocess.CalledProcessError as e:
            print(f"Error opening file: {e}", file=sys.stderr)
            return None
