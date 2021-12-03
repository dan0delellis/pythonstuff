#!/usr/bin/env python3
import argparse, logging, configparser
from get_loudnorm_params import get_loudnorm_params

#setup logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('ooga.log')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logFormat = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
ch.setFormatter(logFormat)
fh.setFormatter(logFormat)
log.addHandler(ch)
log.addHandler(fh)

#parse arugments
parser = argparse.ArgumentParser()
parser.add_argument(
    '--config',
    dest="config",
    default="settings.conf",
    type=str,
    help="config file to read from. Default=settings.conf "
)
parser.add_argument(
    '--input',
    dest="input",
    help="Source input video file. Will exit with an error if target is not a file.",
    type=str,
    default=""
)
parser.add_argument(
    '--output',
    dest="output",
    help="Destination file for output. Defualt prepends REENCODED- to input file name in same directory.",
    type=str,
    default="REENCODED-"
)
parser.add_argument(
    '--no-overwrite',
    dest="safe",
    help="Prevents overwriting existing files with the output. Conflicts will end the program.",
    default=False,
    action="store_true"
)
parser.add_argument(
    '--move-done-files',
    dest="old-files",
    help="Move completed files to a .old directory in same directory as the settings.json file",
    default=False,
    action="store_true"
)

args = parser.parse_args()
print(args)

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.sections()
config.read(args.config)

### Done with args/config/logging

resolutions = {
    "480p" : "640:480",
    "720p" : "1280:720",
    "1080p" : "1920:1080",
    "4k"    : "3840:2160",
}

def show_params(parameters):
    log.debug(f'parameters so far: {parameters}')

def add_arg(params,arglist):
    if isinstance(arglist,str):
        params.extend([arglist])
        return params
    for x in arglist:
        params.append(x)
    return params

def parse_time_options():
    parameters = []
    log.info("Parsing time options")
    time_config=config['time']

    iss = time_config['introSkipSeconds']
    tts = time_config['totalTimeSeconds']
    if float(iss) > 0:
        parameters = add_arg(parameters, ['-ss', iss])
    log.debug(f'parameters so far: {parameters}')

    if float(tts) > 0:
        parameters = add_arg(parameters, ['-t', tss])
    log.debug(f'parameters so far: {parameters}')
    return parameters

def parse_video_options():
    parameters = []
    log.info("Parsing video options")
    v = config['video']
    v_min = v['videoMinRate']
    v_max = v['videoMaxRate']
    v_buf = v['videoBufSize']
    tune = v['tune']

    if v['justCopy'].lower() == "true":
        parameters = add_arg(parameters, ["-c:v", "copy"])
        return parameters

    if v['rasPiHardwareEncode'].lower() == "true":
        parameters = add_arg(parameters, ["-c:v", "h264_omx", "-profile:v", "high"])
        return parameters

    parameters = add_arg(parameters, ["-c:v", "libx264", "-profile:v", "high10"])
    if v['mode'].lower == 'cbr':
        parameters = add_arg(parameters, ["-b:v", v["bitRate"]])
        if v_max != "" and v_buf != "":
            parameters = add_arg(parameters, ["-maxrate", v_max])
            parameters = add_arg(parameters, ["-bufsize", v_buf])
        if v_min != "":
            parameters = add_arg(parameters, ["-minrate", v_min])
    else:
        parameters = add_arg(parameters, ["-crf", v['quality']])

    if tune != "":
        parameters = add_arg(parameters,["-tune", tune])
    log.debug(f'parameters so far: {parameters}')
    return parameters

def parse_audio_options():
    parameters = []
    defaults = dict(codec="aac", bitrate="192k", loudnorm="2pass", channels=2)
    log.info("Parsing audio options")
    a = config['audio']

    #set audio codec
    parameters = add_arg(parameters, ['-c:a'])

    parameters = add_arg(parameters, "boner")

    if a['justCopy']:
        parameters = add_arg(parameters, "copy")
        return parameters

    if a['audioCodec'] != "":
        defaults["codec"] = a['audioCodec']

    parameters = add_arg(parameters, defaults["codec"])

    #set audio bitrate
    parameters = add_arg(parameters, "-b:a")

    if a['audioBitrate'] != "":
        defaults["bitrate"] = a['audioBitrate']

    parameters = add_arg(parameters, defaults["bitrate"])

    #set audio channels
    parameters = add_arg(parameters, "-ac")

    if a['audioChannels'] != "":
        defaults["channels"] = a['audioChannels']

    parameters = add_arg(parameters, defaults["channels"])

    if a["loudnorm"] != False:
        parameters = add_arg(parameters, "-af")
        loudnorm_presets = "I=-16:TP=-1.5:LRA=11"
        loudnorm_filter = f"loudnorm={loudnorm_presets}"
        if a["loudnorm"] == "2pass":
            loudnorm_json = get_loudnorm_params(args.input, loudnorm_presets)

            loudnorm_filter = "{loudnorm_filter}:measured_I={}:measured_LRA={}:measured_TP={}:measured_thresh={}:offset={}:linear=true".format(
                loudnorm_presets,
                loudnorm_json["output_i"],
                loudnorm_json["output_lra"],
                loudnorm_json["output_tp"],
                loudnorm_json["output_thresh"],
                loudnorm_json["target_offset"])
        parameters = add_arg(parameters, loudnorm_filter)

    return parameters

### Start generating input arguments
params = ['ffmpeg','-hide_banner']
if not args.safe:
    params.append('-y')
params = add_arg(params, ["-i", args.input])
show_params(params)

time_params = parse_time_options()
params = add_arg(params, time_params)
show_params(params)

video_params = parse_video_options()
params = add_arg(params, video_params)
show_params(params)

audio_params = parse_audio_options()
params = add_arg(params, audio_params)
show_params(params)
