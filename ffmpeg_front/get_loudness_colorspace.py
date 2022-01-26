#!/usr/bin/env python3
import sys
import subprocess
import re
import json
import os.path

def run_cmd_get_pipes(cmd):
    try:
        pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = pipes.communicate()
    except Exception as e:
        print(e)

    return std_out, std_err

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
    cleaned["master-display"] = 0
    cleaned["light-level"] = 0

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

def get_colorspace_params(filename,fieldlist="frame=color_space,color_primaries,color_transfer,side_data_list,pix_fmt"):
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
    std_out, std_err = run_cmd_get_pipes(cmd)
    json_text = std_out.decode("utf-8")
    full_json = json.loads(json_text)
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

    std_out, std_err = run_cmd_get_pipes(cmd)

    nolines = re.sub(r'\n', "", std_err.decode("utf-8"))

    loudnorm_vals = re.sub(r'.*{','{', nolines)
    print(loudnorm_vals)
    loudnorm_json = json.loads(loudnorm_vals)


    write_json_file(loudnorm_json,json_filename)
    return loudnorm_json

    loudnorm_filter = "{}:measured_I={}:measured_LRA={}:measured_TP={}:measured_thresh={}:offset={}:linear=true".format(
        loudnorm_presets,
        loudnorm_json["output_i"],
        loudnorm_json["output_lra"],
        loudnorm_json["output_tp"],
        loudnorm_json["output_thresh"],
        loudnorm_json["target_offset"])

def write_json_file(data,filename):
    filehandle = open(filename, "w")
    filehandle.write(json.dumps(data,indent=4))
    filehandle.close()

filename = sys.argv[1]
herp = get_colorspace_params(filename)
for key in herp:
    print(f"{key}: {herp[key]}")

#get_loudnorm_params(filename,"I=-16:TP=-1.5:LRA=11")
