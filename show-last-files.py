#!/usr/bin/env python3
import os
import sys
from lib import ezlib as ezlib

from file_read_backwards import FileReadBackwards
import tkinter as tk
from tkinter import simpledialog

gui = None
file_name_filter = None
filter_max_searched_cmds = 500
last_files_amount = 10
recent_dirs_amount = 20


def parse_view_mode():
    global gui
    if len(sys.argv) > 1:
        gui = sys.argv[1]
        if not (gui == "gui" or gui == "terminal"):
            # popup will only work with gui option
            print("usage: python3 show-last-files.py gui|terminal { [filter={ <file_name_filter> | popup } [max_searched_cmds] [recent_dirs_amount] | [last-files-amount] [recent_dirs_amount] } ")
            exit(1)

# find last files amount and recent dirs amount if present in cli args
def parse_last_files_amount(index):
    global last_files_amount
    if len(sys.argv) > index:
        last_files_amount = int(sys.argv[index])

def parse_recent_dirs_amount(index):
    global recent_dirs_amount
    if len(sys.argv) > index:
        recent_dirs_amount = int(sys.argv[index])

def parse_max_searched_cmds(index):
    global filter_max_searched_cmds
    if len(sys.argv) > index:
        filter_max_searched_cmds = int(sys.argv[index])


def show_popup():
    # Create the main application window
    root = tk.Tk()
    root.withdraw()  # Hide the main window, leaving only the popup dialog

    # Show a popup dialog to input the value
    user_input = simpledialog.askstring("Input", "Enter filter:")

    root.destroy()
    # Check if the user provided a value
    if user_input is None:
        print("Error no user input")
        exit(1)
    else:
        return user_input


parse_view_mode()
if len(sys.argv) > 2:
    arg2 = sys.argv[2]
    if arg2.startswith("filter="):
        print("using filename filter")
        file_name_filter=arg2[len("filter="):]
        if file_name_filter == "popup":
            if gui is False:
                print("popup only works in combination with gui")
                exit(1)
            # ask for filter by displaying popup
            file_name_filter = show_popup()
        print("using file name filter: %s" % file_name_filter)
        parse_max_searched_cmds(3)
        parse_recent_dirs_amount(4)
    else:
        print("not using filter")
        parse_last_files_amount(2)
        parse_recent_dirs_amount(3)


def use_filter():
    return file_name_filter is not None


import signal
def sigint_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)


cmd_history_file = os.getenv("HISTFILE")
dir_history_file = os.getenv("DIR_HISTORY")

if gui is None:
    gui = os.getenv("EZ_BASH_GUI")
    if gui is None:
        print("env var EZ_BASH_GUI not set and no gui arg supplied, defaulting to terminal selection")
        gui = "terminal"

if cmd_history_file is None:
    print("cant find cmd history file. Please set env var HISTFILE")
    exit(1)


def check_and_add_file(files, already_seen, file, file_name_filter):
    if os.path.isfile(file):
        print("file exists on system")
        if file in files:
            print("already locally seen")
            return False
        if file in already_seen:
            print("already gloabally seen")
            return False
        print("found file: %s" % file)
        match = True
        if file_name_filter is not None:
            if file_name_filter not in file:
                print("not using file, because filtered out")
                match = False
        if match:
            files.append(file)
            return True
        else:
            return False
    return False


checked_cmds = []

# does not find "files like this" or "files\ like\ this"
def extract_files_from_command(cmd, recent_dirs, recent_files, file_name_filter=None):
    print("checking cmd for files: %s" % cmd)
    global checked_cmds
    # dont parse same cmd twice
    if cmd in checked_cmds:
        return []
    else:
        checked_cmds.append(cmd)


    files = []
    cmd_parts = cmd.replace(";"," ").split(" ")
    for potential_file in cmd_parts:
        try:
            if potential_file.isspace() or potential_file.strip() == "":
                print("skipping part bc only whitespace")
                continue
            file = potential_file.rstrip()
            file = file.replace("../","")
            if file.startswith("/"):
                print("checking potential abs file: %s" % file)
                check_and_add_file(files, recent_files, file, file_name_filter)
                continue
            elif potential_file.startswith("~"):
                print("checking potential abs file: %s" % file)
                file = os.getenv("HOME")+potential_file[1:]
                check_and_add_file(files, recent_files, file, file_name_filter)
                continue
            elif potential_file.startswith("./"):
                file = potential_file[2:]
            # potential relative file, always not starting with /
            print("potential relative file suffix: %s" % file)
            if file.isspace() or file.strip() == "":
                print("skipping part bc only whitespace")
                continue
            print("#####################################################")
            for recent_dir in recent_dirs:
                print("checking recent dir: %s" % recent_dir)
                rel_file = recent_dir+"/"+file
                print("checking potential relative file: %s" % rel_file)
                if check_and_add_file(files, recent_files, rel_file, file_name_filter):
                    break
            print("#####################################################")
        except ValueError as e:
            print("error occured, skipping")
            print(e)
            continue
    return files


def find_recent_files_in_commands(n, recent_dirs):
    global checked_cmds
    checked_cmds = []
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

# finds all files matching file filter like 'grep <my_filter>'
# of n recent dirs
def find_recent_filtered_files_in_commands(file_name_filter,max_searched_cmds, recent_dirs):
    global checked_cmds
    checked_cmds = []
    recent_files = []
    with FileReadBackwards(cmd_history_file) as file:
        while len(checked_cmds) < max_searched_cmds:
            recent_command = file.readline()
            if recent_command == "":
                break
            files = extract_files_from_command(recent_command, recent_dirs, recent_files, file_name_filter=file_name_filter)
            recent_files.extend(files)
        file.close()
    return recent_files


recent_dirs = []
if dir_history_file:
    recent_dirs = ezlib.find_recent_dirs(dir_history_file,recent_dirs_amount)

print("recent dirs")
print(recent_dirs)

if use_filter():
    last_files = find_recent_filtered_files_in_commands(file_name_filter, filter_max_searched_cmds, recent_dirs)
else:
    last_files = find_recent_files_in_commands(last_files_amount, recent_dirs)

print("last files: ")
print(last_files)

if gui == "gui":
    selected_file = ezlib.show_gui_selection(last_files)
else:
    selected_file = ezlib.show_terminal_selection(last_files)

print("selected_file: %s" % selected_file)
if selected_file is None:
    exit(0)
ezlib.put_to_clipboard(selected_file)



