import sys

from file_history.mode import Mode


def eval_mode():
    if len(sys.argv) <= 1:
        return Mode.DEFAULT
    mode_arg = sys.argv[1]
    if mode_arg.startswith("--") or mode_arg.startswith("-"):
        return Mode.DEFAULT
    if mode_arg == Mode.TRACK.value:
        return Mode.TRACK
    if mode_arg == Mode.CLEAN.value:
        return Mode.CLEAN
    else:
        return None

