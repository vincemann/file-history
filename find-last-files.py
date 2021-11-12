# from pwn import *
import os
import sys
from file_read_backwards import FileReadBackwards

if len(sys.argv) > 1:
    last_files_amount = int(sys.argv[1])
else:
    last_files_amount = 10
if len(sys.argv) > 2:
    recent_dirs_amount = int(sys.argv[2])
else:
    recent_dirs_amount = 20

cmd_history_file = os.getenv("HISTFILE")
dir_history_file = os.getenv("DIR_HISTORY")

if cmd_history_file is None:
    print("cant find cmd history file. Please set env var HISTFILE")
    exit(1)


def find_recent_dirs(n):
    recent_dirs = []
    if dir_history_file:
        with open(dir_history_file, 'r') as file:
            while len(recent_dirs) < n :
                recent_dir = file.readline()
                if recent_dir == "":
                    break
                recent_dirs.append(recent_dir.rstrip())
            file.close()
    return recent_dirs


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


recent_dirs = []
if dir_history_file:
    recent_dirs = find_recent_dirs(recent_dirs_amount)

print("recent dirs")
print(recent_dirs)

last_files = find_recent_files_in_commands(last_files_amount, recent_dirs)

print("last files: ")
print(last_files)

