import re

from file_history.logging_config import configure_logger


# extracts files from mix of recent dirs and bash history lines
# for each command scanned, that resulted in found files, the given callback is called
class Parser:

    # recent_dirs must not end with /
    # /path/to/dir is good
    # /path/to/dir/ is not
    def __init__(self, recent_dirs, n, command_parser):
        self.recent_dirs = recent_dirs
        self.n = n
        self.command_parser = command_parser
        self.logger = configure_logger(self.__class__.__name__)
        self.files = []
        self.cmds_seen = []

    def find_files(self, history_lines, callback, filter=None):
        for cmd in history_lines:
            if self.skip_cmd(cmd):
                continue
            self.cmds_seen.append(cmd)
            files_in_cmd = self.command_parser.find_files_in_command(cmd, self.recent_dirs)
            # only add valid, unfiltered and unseen files into result set
            filtered = self.filter_files(self.files, files_in_cmd, filter)
            self.process_files(filtered, callback)

    def skip_cmd(self, cmd):
        if not cmd.strip():
            return True
        # already seen
        if cmd in self.cmds_seen:
            return True
        return False

    def eval_files_cap(self):
        return self.n - len(self.files)

    def found_enough_files(self, files_to_add):
        if self.n is not None and len(self.files)+len(files_to_add) >= self.n:
            return True
        else:
            return False

    def filter_files(self, already_seen, files, filter_pattern):
        result = []
        for file in files:
            # Don't add files twice
            if file in already_seen:
                continue
            # apply filter
            if filter_pattern and not re.search(filter_pattern, file):
                continue
            result.append(file)
        return result

    def process_files(self, files_to_add, callback):
        if len(files_to_add) == 0:
            return
        if self.found_enough_files(files_to_add):
            cap = self.eval_files_cap()
            self.send_to_callback(files_to_add[:cap], callback)
            return
        else:
            self.send_to_callback(files_to_add, callback)

    def send_to_callback(self, files_to_add, callback):
        if len(files_to_add) == 0:
            return
        self.files.extend(files_to_add)
        callback(files_to_add)


