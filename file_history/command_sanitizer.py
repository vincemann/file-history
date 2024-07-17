

BASH_SYMBOLS = [">", ">>", "<", "<<"]


# removes everything from command that for sure is not a file
# for example: prepending sudo and program name, special bash characters or --args
class CommandSanitizer:

    @staticmethod
    def remove_non_file_parts(cmd_parts):
        file_candidate_cmd_parts = []

        if len(cmd_parts) == 0:
            return []
        # skip sudo and program name
        i = CommandSanitizer.eval_initial_skip_count(cmd_parts)

        while i < len(cmd_parts):
            part = cmd_parts[i]

            if part in BASH_SYMBOLS:
                i += 1
                continue

            # skip args like -v or --verbose
            if part.startswith("-"):
                i += 1
                continue

            if part == "sudo":
                i += 2  # Skip 'sudo' and the next command
                continue

            # this may be a file, so add
            file_candidate_cmd_parts.append(part)
            i += 1

        return file_candidate_cmd_parts

    @staticmethod
    def eval_initial_skip_count(cmd_parts):
        first_part = cmd_parts[0]
        if first_part == "sudo" and len(cmd_parts) > 1:
            return 2
        else:
            return 1