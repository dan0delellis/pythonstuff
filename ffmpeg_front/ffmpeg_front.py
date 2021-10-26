#!/usr/bin/env python3
import argparse, logging, configparser

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
    help="config file to read from. Default=settings.conf in single-file mode. settings.conf in source directory if --directory is used."
)
parser.add_argument(
    '--input',
    dest="input",
    help="Source input video file. Source directory if --directory is used. Will exit with an error if target is not a file or directory.",
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
    '--destination-directory',
    dest="destination",
    help="Destination directory for file output. Default is current working directory.",
    default="",
    type=str
)
parser.add_argument(
    '--directory',
    dest="directory",
    help="Process all files found in a target directory. If --input is omitted, will assume current working directory. If --input specifies a non-directory (either a file or an invalid path), program will exit with an error. Ignores --output flag. Output files will have REENCODED- prepended to the filename if --destination-directory is not specified.",
    default=False,
    action="store_true"
)
parser.add_argument(
    '--no-overwrite',
    dest="safe",
    help="Prevents overwriting existing files with the output. Conflicts will end the program, or proceed to the next file if working in directory mode.",
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

### Start generating input arguments
params = ['-hide_banner', '-i']
if not args.safe:
    params.append('-y')
log.debug(f'parameters so far: {params}')


def parse_time_options(parameters):
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

def parse_video_options(parameters):
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


