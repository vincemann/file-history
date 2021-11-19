#!/usr/bin/env python3
import os
import sys
from lib import ezlib as ezlib

from file_read_backwards import FileReadBackwards

gui = None
ezlib.init_logfile("cd-history.log")

if len(sys.argv) > 1:
    gui = sys.argv[1]
    if not (gui == "gui" or gui == "terminal"):
        print("usage: python3 show-last-files.py gui|terminal [last-files-amount ; [recent_dirs_amount]] ")
        exit(1)
if len(sys.argv) > 2:
    last_files_amount = int(sys.argv[2])
else:
    last_files_amount = 10
if len(sys.argv) > 3:
    recent_dirs_amount = int(sys.argv[3])
else:
    recent_dirs_amount = 20



cmd_history_file = os.getenv("HISTFILE")
dir_history_file = os.getenv("DIR_HISTORY")

if gui is None:
    gui = os.getenv("EZ_BASH_GUI")
    if gui is None:
        print("env var EZ_BASH_GUI not set and no gui arg supplied, defaulting to terminal selection box")
        gui = "terminal"

if cmd_history_file is None:
    print("cant find cmd history file. Please set env var HISTFILE")
    exit(1)


def check_and_add_file(files, already_seen, file):
    if os.path.isfile(file):
        if file not in files and file not in already_seen:
            print("found file: %s" % file)
            files.append(file)
            return True
    return False


def extract_files_from_command(cmd, recent_dirs, recent_files):
    print("checking cmd for files: %s" % cmd)
    cmd_parts = cmd.split(" ")
    files = []
    for potential_file in cmd_parts:
        try:
            if len(potential_file) == 0:
                continue
            file = potential_file.rstrip()
            if file.startswith("/"):
                # print("checking potential file: %s" % file)
                check_and_add_file(files, recent_files, file)
            elif potential_file.startswith("./"):
                file = potential_file[1:]
            # potential relative file

            # print("#####################################################")
            for recent_dir in recent_dirs:
                file = recent_dir+"/"+file
                # print("checking potential file: %s" % file)
                if check_and_add_file(files, recent_files, file):
                    break
            # print("#####################################################")
        except ValueError as e:
            print("error occured, skipping")
            print(e)
            continue
    return files


def find_recent_files_in_commands(n, recent_dirs):
    recent_files = []
    with FileReadBackwards(cmd_history_file) as file:
        while len(recent_files) < n:
            recent_command = file.readline()
            if recent_command == "":
                break
            files = extract_files_from_command(recent_command, recent_dirs,recent_files)
            recent_files.extend(files)
        file.close()
    return recent_files

import signal
def sigint_handler(signal, frame):
    sys.exit(0)

recent_dirs = []
if dir_history_file:
    recent_dirs = find_recent_dirs(dir_history_file,recent_dirs_amount)

print("recent dirs")
print(recent_dirs)

last_files = find_recent_files_in_commands(last_files_amount, recent_dirs)

print("last files: ")
print(last_files)

if gui == "gui":
    selected_file = ezlib.show_gui_selection(last_files)
else:
    selected_file = ezlib.show_terminal_selection(last_files)

print("selected_file: %s" % selected_file)
ezlib.put_to_clipboard(selected_file)



