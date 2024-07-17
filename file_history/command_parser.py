from file_history.logging_config import configure_logger
from file_history.file_path_resolver import FilePathResolver
from file_history.command_splitter import CommandSplitter
from file_history.command_sanitizer import CommandSanitizer
from file_history.utils import flatten_strings_list


# extracts files operated on in command
class CommandParser:

    def __init__(self, file_checker):
        self.file_checker = file_checker
        self.logger = configure_logger(self.__class__.__name__)
        self.command_splitter = CommandSplitter()

    def find_files_in_command(self, cmd, recent_dirs):
        self.logger.debug("checking cmd for files: '%s'" % cmd.rstrip())

        files = []
        cmd_parts = self.command_splitter.split_command(cmd)
        # single word commands cannot contain file
        if len(cmd_parts) <= 1:
            return []
        cmd_parts = flatten_strings_list(cmd_parts)
        self.logger.debug("split cmd: " + str(cmd_parts))
        for sub_cmd in cmd_parts:
            self.logger.debug("sub cmd: " + str(sub_cmd))
            if self.skip_sub_cmd(sub_cmd):
                self.logger.debug("cant contain file, skipping")
                continue
            _sub_cmd = CommandSanitizer.remove_non_file_parts(sub_cmd)
            self.logger.debug("sanitized sub cmd: " + str(_sub_cmd))
            for file_candidate in _sub_cmd:
                _file_candidate, _recent_dirs = self.resolve_relative_dirs(file_candidate.rstrip(), recent_dirs)

                if _file_candidate.isspace() or _file_candidate.strip() == "":
                    continue
                if _file_candidate.startswith("/"):
                    self.logger.debug("checking potential abs file: %s" % _file_candidate)
                    self.add_if_exists(files, _file_candidate)
                    continue
                for recent_dir in _recent_dirs:
                    rel_file = recent_dir + "/" + _file_candidate
                    self.logger.debug("checking potential recent_dir/file combination: %s" % rel_file)
                    self.add_if_exists(files, rel_file)
        return files

    # checks if command like ["echo", "gil"] can even contain a file
    # if its not possible return true -> dont further scan cmd
    def skip_sub_cmd(self, sub_cmd):
        if len(sub_cmd) == 0:
            return True
        # List of commands that typically don't operate on files
        ignored_commands = [
        "cd", "pwd", "exit", "echo", "clear", "logout", "history",
        "set", "unset", "alias", "unalias", "export", "source", "trap",
        "fg", "bg", "jobs", "kill", "disown", "wait", "shift", "times",
        "help", "type", "true", "false", "test", "local", "readonly"
        ]
        # Check if the command part is in the list of ignored commands
        # but dont skip cmd if contains right aimed redirect like echo "foo" > myfile.txt
        return (sub_cmd[0] in ignored_commands) and not self.contains_redirect(sub_cmd)

    def contains_redirect(self, cmd_parts):
        redirects = [">", ">>"]
        return any(redirect in cmd_parts for redirect in redirects)

    # adjusts file and recent dirs in order to resolve ../ ./ & ~/ paths
    def resolve_relative_dirs(self, file, recent_dirs):
        # resolve paths like "~/myfile.txt"
        _file = FilePathResolver.resolve_home_directories(file)
        # resolve paths like "../../myfile.txt"
        _file, _recent_dirs = FilePathResolver.resolve_parent_directories(recent_dirs, _file)
        # resolve paths like "./myfile.txt"
        _file = FilePathResolver.resolve_dot_slash_directories(_file)
        return _file, _recent_dirs

    def add_if_exists(self, files, file):
        if self.file_checker.isfile(file):
            self.logger.debug("found file: %s" % file)
            files.append(file)
        else:
            self.logger.debug("file %s does not exist" % file)
