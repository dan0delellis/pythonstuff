#!/usr/bin/env python3
import argparse, logging, configparser
from get_loudnorm_params import get_loudnorm_params

#setup logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('ooga.log')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
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

### Start generating input arguments
params = ('-hide_banner')
if not args.safe:
    params.append('-y')
show_params(params)

time_params = parse_time_options()
params.append(time_params)
show_params(params)

video_params = parse_video_options()
params.append(video_params)
show_params(params)

audio_params = parse_audio_options()
params.append(audio_params)
show_params(params)


def parse_time_options():
    parameters = []
    log.info("Parsing time options")
    time_config=config['time']

    iss = time_config['introSkipSeconds']
    tts = time_config['totalTimeSeconds']
    if iss['introSkipSeconds'] > 0:
        parameters.extend(['-ss', iss])
    log.debug(f'parameters so far: {parameters}')

    if tts > 0:
        parameters.extend(['-t', tss])
    log.debug(f'parameters so far: {parameterss}')
    return parameters

def parse_video_options():
    log.info("Parsing video options")
    v = config['video']
    v_min = v['minRate']
    v_max = v['maxRate']
    v_buf = v['bufSize']
    tune = v['tune']

    if v['justCopy']:
        parameters.extend(["-c:v", "copy"])
        return parameters

    if not v['softwareEncode']:
        parameters.extend(["-c:v", "h264_omx", "-profile:v", "high"])
        return parameters

    parameters.extend(["-c:v", "libx264", "-profile:v", "high10"])
    if not v['crfMode']:
        parameters.extend(["-b:v", v["bitRate"]])
    else:
        parameters.extend(["-crf", v['quality']])

    if v_min != "":
        parameters.extend(["-minrate", v_min])
    if v_max != "":
        parameters.extend(["-maxrate", v_max])
    if tune != "":
        parameters.extend(["-tune"], tune)
    log.debug(f'parameters so far: {parameters}')
    return parameters

def parse_audio_options():
    parameters = []
    defaults = dict(codec="aac", bitrate="192k", loudnorm="2pass", channels=2)
    log.info("Parsing audio options")
    a = config['audio']

    #set audio codec
    parameters.extend("-c:a")

    if a['justCopy']:
        parameters.extend(copy)
        return parameters

    if a['audioCodec'] != "":
        defaults["codec"] = a['audioCodec']

    parameters.extend(defaults["codec"])

    #set audio bitrate
    parameters.extend("-b:a")

    if a['audioBitrate'] != "":
        defaults["bitrate"] = a['audioBitrate']

    parameters.extend(defaults["bitrate"])

    #set audio channels
    parameters.extend("-ac")

    if a['audioChannels'] != "":
        defaults["channels"] = a['audioChannels']

    parameters.extend(defaults["channels"])

    if a["loudnorm"] != False:
        parameters.extend("-af")
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
        parameters.extend(loudnorm_filter)

    return parameters

