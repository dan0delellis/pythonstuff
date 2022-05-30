#!/usr/bin/env python3
import sys
import subprocess
import re
import os, os.path
import shutil
import json

def run_cmd_get_pipes(cmd):
    print(type(cmd))
    if type(cmd) == str:
        cmd = cmd.split()
    try:
        print(cmd)
        pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = pipes.communicate()
        ret = pipes.returncode
    except Exception as e:
        return(ret, e, f"stdout:{std_out}; stderr:{std_err}")

    return ret, std_out, std_err


def in_hidden_dir(path):
    hidden = False
    file_realpath = os.path.abspath(path)
    file_location = os.path.dirname(file_realpath)
    dir_tree = file_location.split("/")
    for leaf in dir_tree:
        hidden = re.search("^\..+$", leaf)
        if hidden:
            return hidden
    return hidden

def create_path_if_needed(path,make_dir_for_filepath=False):
    #If the path is a filename, then we we want to make a home for that file, not make a directory with that filename
    if make_dir_for_filepath:
        path=os.path.dirname(path)

    dir_realpath = os.path.abspath(path)

    if not os.path.exists(dir_realpath):
        dir_info = os.stat(dir_realpath)
        os.mkdir(dir_realpath, mode=file_dir_info.st_mode)
        os.chown(dir_realpath, uid=file_dir_info.st_uid, gid=file_dir_info.st_gid)

def check_video_stream(path):
    success = False
    cmd = f"/usr/bin/ffprobe -show_entries stream=width,height -of json -v quiet -i {path}"
    ret, std_out, std_err = run_cmd_get_pipes(cmd)
    if type(std_out) == "Exception":
        return success

    json_text = std_out.decode("utf-8")
    full_json = json.loads(json_text)
    for stream in full_json['streams']:
        if "height" in stream.keys() and "width" in stream.keys():
            success = True
            return success

    return success

def feed_to_ffmpeg_front(CONFIG, INPUT, OUTPUT, LOG_FILE,move_done=False,ffront_path="/usr/bin/ffmpeg_front.py"):
    success = False
    move_done_files = ""
    if move_done:
        move_done_files = "--move-done-files"
    cmd = f"{ffront_path} --config {CONFIG} --input {INPUT} --output {OUTPUT} --no-overwrite {move_done_files} --log-file {LOG_FILE}"
    ret, std_out, std_err = run_cmd_get_pipes(cmd)
    if ret != 0 or std_err != b'':
        print(f"Issue running cmd: exit code {ret}, std_err:{std_err}")
    else:
        success = True
    return success

def move_file(source_file, dest_file):
    file_full_path = os.path.abspath(source_file)
    dest_full_path = os.path.abspath(dest_file)
    create_path_if_needed(dest_full_path, make_dir_for_filepath=True)
    try:
        shutil.move(file_full_path, old_file_path)
    except Exception as e:
        return(e)

    return(f"Moved `{file_full_path}` to `{dest_file_path}`")
