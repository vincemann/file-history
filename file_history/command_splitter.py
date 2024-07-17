import re
import shlex
from file_history.logging_config import configure_logger

# Known commands and their options that indicate a subshell
subshell_indicators = {
    "bash": "-c",
    "sh": "-c",
    "csh": "-c",
    "tcsh": "-c",
    "ksh": "-c",
    "zsh": "-c",
    "dash": "-c",
    "runuser": "-c",
    "sudo": "-c",
}

new_cmd_delimiter = [";", "|", "&&"]


# split command into list of subcommands
# each subcommand is a list of cmd_parts like [ls, foo.txt]
# supports subshells and command chains with ; or | or &&
# -> "ls foo | grep bar" becomes [[ls,foo],[grep, bar]]
# swallows subshell prefixes
# -> "bash -c 'ls foo.txt'" becomes [ls, foo.txt]
class CommandSplitter:

    def __init__(self):
        self.logger = configure_logger(self.__class__.__name__)

    def split_command(self, cmd):
        try:
            cmd_parts = CommandSplitter.shlex_split(cmd)
            # split [cd, foo, ;, cd, bar] into [cd, foo], [cd, bar]
            cmd_parts = CommandSplitter.split_list_by_del(cmd_parts, new_cmd_delimiter)

            # find subshell parts, those need to be removed from cmd_parts and split separately
            pos = 0
            for inner_cmd in cmd_parts:
                subshell_position = CommandSplitter.find_sub_shell_position(inner_cmd)
                if subshell_position is not None:
                    subshell = self.split_command(inner_cmd[subshell_position])
                    cmd_parts[pos] = subshell
                pos += 1

            # remove unnecessary list levels
            # if [[ls,foo]] return [ls,foo]
            if len(cmd_parts) == 1:
                return cmd_parts[0]
            return cmd_parts

        except ValueError as e:
            self.logger.debug(f"Error splitting command: {e}")
            return []

    @staticmethod
    def shlex_split(cmd):
        _cmd = CommandSplitter.ensure_spaces_around_delimiters(cmd, ";")
        return shlex.split(_cmd)

    @staticmethod
    def ensure_spaces_around_delimiters(input_string, delimiters):
        # Create a regular expression pattern that matches any of the delimiters
        pattern = f"({'|'.join(map(re.escape, delimiters))})"

        # Use the re.sub function to add spaces around the delimiters
        result = re.sub(pattern, r' \1 ', input_string)

        # Remove any extra spaces (e.g., if there were already spaces around the delimiters)
        result = re.sub(r'\s+', ' ', result).strip()

        return result

    @staticmethod
    def split_list_by_del(input_list, delimiters):
        result = []
        current_sublist = []

        for item in input_list:
            if item in delimiters:
                if current_sublist:
                    result.append(current_sublist)
                    current_sublist = []
            else:
                current_sublist.append(item)

        if current_sublist:
            result.append(current_sublist)

        return result

    # find pos in cmd_parts where a subshell is located
    @staticmethod
    def find_sub_shell_position(cmd_parts):
        next_sub_shell_part = False
        sub_shell_positions = []
        pos = 0

        while pos < len(cmd_parts):
            part = cmd_parts[pos]
            if part in subshell_indicators:
                option = subshell_indicators[part]
                if pos + 1 < len(cmd_parts) and cmd_parts[pos + 1] == option:
                    next_sub_shell_part = True
                    pos += 1  # Skip the option part
                else:
                    next_sub_shell_part = False
            elif next_sub_shell_part:
                # Check if quotes are present at both ends of the part
                sub_shell_positions.append(pos)
                next_sub_shell_part = False
            pos += 1
        # dont support nested shells
        if len(sub_shell_positions) == 0:
            return None
        else:
            return sub_shell_positions[0]

