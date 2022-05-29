#!/usr/bin/env python3
import sys
import subprocess
import re
import os, os.path
import shutil
import json

def run_cmd_get_pipes(cmd):
    if type(cmd) == str:
        cmd = cmd.split()
    try:
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

def create_path_if_needed(path):
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

def feed_to_ffmpeg_front(ffront_path,CONFIG, INPUT, OUTPUT, move_done, LOG_FILE):
    success = False
    move_done_files = ""
    if move_done:
        move_done_files = "--move-done-files"
    cmd = f"{ffront_path} --config {CONFIG} --input {INPUT} --output {OUTPUT} --no-overwrite {move_done_files} --log-file {LOG_FILE}"
    ret, std_out, std_err = run_cmd_get_pipes(cmd)

