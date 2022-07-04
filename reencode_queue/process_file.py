#!/usr/bin/env python3
import sys
import subprocess
import re
import os, os.path
import shutil
import json


def logger(msg):
    cmd = ["logger", "-s", msg]
    _,_,std_err = run_cmd_get_pipes(cmd)
    print(std_err)

def run_cmd_get_pipes(cmd):
    if type(cmd) == str:
        cmd = cmd.split()

    if cmd[0] != "logger":
        logger(f"EXEC:    {cmd}")
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

def create_path_if_needed(path,template_dir=".",make_dir_for_filepath=False):
    logger(f"Checking if {path} needs to be created")

    #If the path is a filename, then we we want to make a home for that file, not make a directory with that filename
    if make_dir_for_filepath:
        logger("The path provided is a file. Getting the dir tree for where the file lives.")
        path=os.path.dirname(path)

    dir_realpath = os.path.abspath(path)
    logger(f"The real path is :{dir_realpath}")

    if not os.path.exists(dir_realpath):
        dir_info = os.stat(template_dir)
        logger(f"Attempting to create dir: `{dir_realpath}`")
        os.makedirs(dir_realpath, mode=dir_info.st_mode)
        os.chown(dir_realpath, uid=dir_info.st_uid, gid=dir_info.st_gid)

def check_video_stream(path,fprobe_path="/usr/bin/ffprobe"):
    if fprobe_path=="/bin/true":
        return True
    success = False
    cmd = f"{fprobe_path} -show_entries stream=width,height -of json -v quiet -i {path}"
    ret, std_out, std_err = run_cmd_get_pipes(cmd)
    if type(std_out) == "Exception":
        return success

    json_text = std_out.decode("utf-8")
    full_json = json.loads(json_text)
    try:
        for stream in full_json['streams']:
            if "height" in stream.keys() and "width" in stream.keys():
                success = True
    except:
        logger(f"{path} is not a video file")

    return success

def feed_to_ffmpeg_front(CONFIG, INPUT, OUTPUT, LOG_FILE,move_done=False,ffront_path="/usr/bin/ffmpeg_front.py"):
    success = False
    move_done_files = ""
    if move_done:
        move_done_files = "--move-done-files"
    cmd = f"{ffront_path} --config {CONFIG} --input {INPUT} --output {OUTPUT} --no-overwrite {move_done_files} --log-file {LOG_FILE}"
    logger(cmd)
    ret, std_out, std_err = run_cmd_get_pipes(cmd)
    if ret != 0:
        print(f"Issue running cmd: exit code {ret}, std_err:{std_err}")
    else:
        success = True

    result = {
        "succeeded" : success,
        "std_out"   : std_out,
        "std_err"   : std_err
    }

    return result

def move_file(testing, source_file, dest_file):
    if testing:
        logger(f"not actually moving {source_file} to {dest_file} because testing")
    file_full_path = os.path.abspath(source_file)
    dest_full_path = os.path.abspath(dest_file)
    create_path_if_needed(dest_full_path, make_dir_for_filepath=True)
    try:
        shutil.move(file_full_path, dest_full_path)
    except Exception as e:
        logger(e)
        return(e)

    return(f"Moved `{file_full_path}` to `{dest_full_path}`")

def make_template(template):
    tv_normal = {
        "video": {
        	"rasPiHardwareEncode":False,
        	"justCopy":False,
        	"videoCodec":"libx265",
        	"videoProfile":"main10",
        	"retainHDR":True,
        	"preset":"slow",
        	"resolution":"720p",
        	"mode":"crf",
        	"quality":"23",
        	"tune":"false",
        	"videoBitrate":"3M",
        	"videoMinRate":"1M",
        	"videoMaxRate":"6M",
        	"videoBufsize":"6M",
        	"otherFilters":False,
        },
        "audio": {
        	"justCopy":False,
        	"audioCodec":"aac",
        	"audioChannels":2,
        	"audioBitrate":"200k",
        	"loudnorm":"2pass",
        },
        "subtitles": {
        	"burnInSubtitles":False,
        	"subtitleExternalFile":False,
        	"subtitleStyle":False,
        	"subtitleStream":1,
        },
        "time": {
        	"introSkipSeconds":0,
        	"totalTimeSeconds":0,

        }
    }
    tv_high = {
        "video": {
        	"rasPiHardwareEncode":False,
        	"justCopy":False,
        	"videoCodec":"libx265",
        	"videoProfile":"main10",
        	"retainHDR":True,
        	"preset":"slow",
        	"resolution":"1080p",
        	"mode":"crf",
        	"quality":"21",
        	"tune":"false",
        	"videoBitrate":"4M",
        	"videoMinRate":"1M",
        	"videoMaxRate":"6M",
        	"videoBufsize":"6M",
        	"otherFilters":False,
        },
        "audio": {
        	"justCopy":False,
        	"audioCodec":"aac",
        	"audioChannels":2,
        	"audioBitrate":"200k",
        	"loudnorm":"2pass",
        },
        "subtitles": {
        	"burnInSubtitles":False,
        	"subtitleExternalFile":False,
        	"subtitleStyle":False,
        	"subtitleStream":1,
        },
        "time": {
        	"introSkipSeconds":0,
        	"totalTimeSeconds":0,

        }
    }

    movie = {
        "video": {
        	"rasPiHardwareEncode":False,
        	"justCopy":True,
        },
        "audio": {
        	"justCopy":False,
        	"audioCodec":"aac",
        	"audioChannels":2,
        	"audioBitrate":"200k",
        	"loudnorm":"2pass",
        },
        "subtitles": {
        	"burnInSubtitles":False,
        	"subtitleExternalFile":False,
        	"subtitleStyle":False,
        	"subtitleStream":1,
        },
        "time": {
        	"introSkipSeconds":0,
        	"totalTimeSeconds":0,
        }
    }

    templates = {
        "tv-normal" : tv_normal,
        "tv-high" : tv_high,
        "movie" : movie,
        "movies": movie,
    }
    for section in templates[template].keys():
        temp = templates[template][section]
        print(f"[{section}]")
        for key in temp.keys():
            print(f"{key} = {temp[key]}")
        print("")
