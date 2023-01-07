#!/usr/bin/env python3
import sys
import subprocess
import re
import json
import os, os.path
import shutil

def move_done_file(input_file):
    file_full_path = os.path.abspath(input_file)
    file_dir_path = os.path.dirname(file_full_path)
    file_dir_info = os.stat(file_dir_path) #st_uid, st_gid, st_mode
    old_dir_path = f"{file_dir_path}/.old"
    old_file_path = f"{old_dir_path}/{input_file}"
    try:
        if not (os.path.exists(old_dir_path)):
            os.mkdir(old_dir_path, mode=file_dir_info.st_mode)
            os.chown(old_dir_path, uid=file_dir_info.st_uid, gid=file_dir_info.st_gid)

        shutil.move(file_full_path, old_file_path)
    except Exception as e:
        return(e)

    return(f"Moved `{file_full_path}` to `{old_file_path}`")

def run_cmd_get_pipes(cmd):
    try:
        pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = pipes.communicate()
        ret = pipes.returncode
    except Exception as e:
        return(ret, e, f"stdout:{std_out}; stderr:{std_err}")

    return ret, std_out, std_err

def force_denom(v, d):
    p = v.split("/")
    if int(p[1]) == d:
        return p[0]
    else:
        print(v)
        r = float(p[0]) / float(p[1])
        n = int(d * r)
        return n

def clean_data(data):
    cleaned = data
    denom_50k = [
        "red_x",
        "red_y",
        "green_x",
        "green_y",
        "blue_x",
        "blue_y",
        "white_point_x",
        "white_point_y"]

    denom_10k = [
        "min_luminance",
        "max_luminance"
    ]
    int_val = [
        "max_content",
        "max_average"
    ]
    cleaned["master-display"] = True
    cleaned["light-level"] = True

    for i in denom_50k:
        if i in data:
            cleaned[i] = force_denom(data[i],50000)
        else:
            cleaned["master-display"] = False

    for i in denom_10k:
        if i in data:
            cleaned[i] = force_denom(data[i],10000)
        else:
            cleaned["master-display"] = False

    for i in int_val:
        if not i in data:
            cleaned["light-level"] = False

    return cleaned

def flatten_json(y):
    out = {}

    def flatten(x, name =''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], a)

        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, a)
                i += 1
        else:
            out[name] = x

    flatten(y)
    out = clean_data(out)
    return out

def make_json_output(cmd):
    returncode, std_out, std_err = run_cmd_get_pipes(cmd)
    if type(std_out) == "Exception":
       return False

    json_text = std_out.decode("utf-8")
    full_json = json.loads(json_text)
    return full_json


def get_sample_rate(filename):
    cmd = f'ffprobe -show_entries stream=sample_rate -of json -v error -i {filename}'.split()
    full_json = make_json_output(cmd)
    for stream in full_json["streams"]:
        if stream != {}:
            return(stream['sample_rate'])

    return False

def get_colorspace_params(filename,fieldlist="frame=color_space,color_primaries,color_transfer,side_data_list,pix_fmt"):
    print(filename)
    data = {}

    cmd = ['ffprobe',
        '-hide_banner',
        '-loglevel',
        'warning',
        '-select_streams',
        'v',
        '-print_format',
        'json',
        '-show_frames',
        '-read_intervals',
        "%+#1",
        '-show_entries',
        fieldlist,
        '-i',
        filename
    ]
    full_json = make_json_output(cmd)
    data = flatten_json(full_json["frames"])
    return(data)

def get_loudnorm_params(filename,loudnorm_presets):
    json_filename = f"{filename}.loudnorm.json"

    if(os.path.exists(json_filename)):
        data_file = open(json_filename, "r")
        data = json.loads(data_file.read())
        return data

    cmd = ["ffmpeg",
        "-hide_banner",
        "-y",
        "-i",
        filename,
        "-vn",
        "-filter:a",
        f"loudnorm={loudnorm_presets}:print_format=json",
        "-f",
        "null",
        "-"]

    print(cmd)

    returncode, std_out, std_err = run_cmd_get_pipes(cmd)

    if type(std_out) == "Exception":
        return std_out

    nolines = re.sub(r'\n', "", std_err.decode("utf-8"))

    loudnorm_vals = re.sub(r'.*{','{', nolines)
    print(loudnorm_vals)
    loudnorm_json = json.loads(loudnorm_vals)


    write_json_file(loudnorm_json,json_filename)
    return loudnorm_json

def write_json_file(data,filename):
    filehandle = open(filename, "w")
    filehandle.write(json.dumps(data,indent=4))
    filehandle.close()

#filename = sys.argv[1]
#herp = get_sample_rate(filename)
#print(herp)
