#!/usr/bin/env python3
import sys
import subprocess
import re
import json
import os.path

def get_loudnorm_params(filename,loudnorm_presets):
    json_filename = f"{filename}.loudnorm.json"

    if(os.path.exists(json_filename)):
        data_file = open(json_filename, "r")
        data = json.loads(data_file.read())
        return data

    cmd = ["ffmpeg",
        "-y",
        "-i",
        filename,
        "-vn",
        "-filter:a",
        f"loudnorm={loudnorm_presets}:print_format=json",
        "-f",
        "null",
        "/dev/null"]

    pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = pipes.communicate()

    nolines = re.sub(r'\n', "", std_err.decode("utf-8"))

    loudnorm_vals = re.sub(r'.*{','{', nolines)
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



#filename = sys.argv[1]
#get_loudnorm_params(filename,"I=-16:TP=-1.5:LRA=11")
