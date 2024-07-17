import sys

from file_history.app_launcher import DefaultAppLauncher
from file_history.clean.clean_app import CleanApp
from file_history.mode import Mode
from file_history.mode_parser import eval_mode
from file_history.track.track_app import TrackApp


def start_default_app():
    launcher = DefaultAppLauncher()
    launcher.start()


def start_track_app():
    app = TrackApp()
    app.start()


def start_clean_app():
    app = CleanApp()
    app.start()


def main():
    mode = eval_mode()
    if mode is None:
        err = "unknown first arg, use either 'file-history clean', 'file-history track dir cmd' "
        "or default mode (type 'file-history -h' for instructions for default mode)"
        print(err, file=sys.stderr)
        exit(1)
    if mode is Mode.DEFAULT:
        start_default_app()
    elif mode is Mode.TRACK:
        start_track_app()
    elif mode is Mode.CLEAN:
        start_clean_app()


if __name__ == "__main__":
    main()
