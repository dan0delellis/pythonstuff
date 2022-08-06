#!/usr/bin/env python3
import argparse, logging, configparser, sys, os.path
from get_loudness_colorspace import get_loudnorm_params, get_colorspace_params, run_cmd_get_pipes, move_done_file

if len(sys.argv) == 1:
    sys.argv.append("--help")


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
    dest="move_old",
    help="Move completed files to a .old directory in same directory as the input file",
    default=False,
    action="store_true"
)
parser.add_argument(
    '--conf-help',
    dest="conf_help",
    help="Show help info for the config file",
    default=False,
    action="store_true"
)
parser.add_argument(
    '--log-file',
    dest="log_file",
    help="path of logfile. Defaults to 'reencoder.log' in path of config file",
    default="",
)

args = parser.parse_args()

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.sections()
config.read(args.config)

#setup logging
log_path = "ooga.log"
log = logging.getLogger()
log.setLevel(logging.INFO)
if (args.log_file == ""):
    log_path = f"{os.path.dirname(os.path.abspath(args.config))}/reencoder.log"
else:
    log_path = args.log_file
fh = logging.FileHandler(log_path)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logFormat = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')
ch.setFormatter(logFormat)
fh.setFormatter(logFormat)
log.addHandler(ch)
log.addHandler(fh)
### Done with args/config/logging

resolutions = {
    "480p" : "640:480",
    "720p" : "1280:720",
    "1080p" : "1920:1080",
    "4k"    : "3840:2160",
}

def is_that_a_no(val):
    ways_to_say_no = ["no", "", "false", "none", False]
    ans = val.lower()
    for x in ways_to_say_no:
        if x == ans:
            return True
    return False


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

    if float(tts) > 0:
        parameters = add_arg(parameters, ['-ts', tts])
    return parameters

def parse_video_options():
    parameters = []
    log.info("Parsing video options")
    v = config['video']
    v_codec = v['videoCodec'].lower()
    v_hdr = v['retainHDR'].lower()
    v_profile = v['videoProfile'].lower()
    v_speed = v['preset'].lower()
    v_min = v['videoMinRate'].lower()
    v_max = v['videoMaxRate'].lower()
    v_buf = v['videoBufSize'].lower()
    tune = v['tune'].lower()
    v_filters = v['otherFilters'].lower()
    resolution = v['resolution'].lower()
    s = config['subtitles']
    burn_subs = s['burnInSubtitles'].lower()

    if not is_that_a_no(v['justCopy']):
        parameters = add_arg(parameters, ["-c:v", "copy"])
        return parameters

    if not is_that_a_no(v['rasPiHardwareEncode']):
        parameters = add_arg(parameters, ["-c:v", "h264_omx", "-profile:v", "high"])
        return parameters

    if not is_that_a_no(v_codec):
        parameters = add_arg(parameters, ["-c:v", v_codec])

    hdr_parms = {}

    if not is_that_a_no(v_hdr):
        hdr_params = parse_hdr_params()
        parameters = add_arg(parameters, ["-x265-params", f'\"{hdr_params["x265-params"]}\"'])

    if is_that_a_no(v_profile):
        parameters = add_arg(parameters, "-profile:v")
        if v_codec == 'libx264':
            parameters = add_arg(parameters, "high10")
        if v_codec == 'libx265' or v_codec == 'hevc':
            parameters = add_arg(parameters, "main10")
    else:
        if v_profile != "default":
            parameters = add_arg(parameters, ["-profile:v", v_profile])

    if v['mode'].lower == 'cbr':
        parameters = add_arg(parameters, ["-b:v", v["bitRate"]])
        if v_max != "" and v_buf != "":
            parameters = add_arg(parameters, ["-maxrate", v_max])
            parameters = add_arg(parameters, ["-bufsize", v_buf])
        if v_min != "":
            parameters = add_arg(parameters, ["-minrate", v_min])
    else:
        parameters = add_arg(parameters, ["-crf", v['quality']])

    parameters = add_arg(parameters, ["-preset", "slow"]) #deal with it, nerd

    if "pix_fmt" in hdr_params:
        parameters = add_arg(parameters, ["-pix_fmt", hdr_params["pix_fmt"]])

    if not is_that_a_no(tune):
        parameters = add_arg(parameters,["-tune", tune])

    filter_set = False
    subs_options = ""
    resolution_options = ""
    other_filters = ""

    if not is_that_a_no(burn_subs):
        filter_set = True
        subs_options = parse_subtitle_options()

    if not is_that_a_no(resolution):
        filter_set = True
        resolution_options = parse_resolution(resolution)

    if not is_that_a_no(other_filters):
        filter_set = True

    if not filter_set:
        return parameters

    filter_list = [subs_options, other_filters, resolution_options]

    while("" in filter_list):
        filter_list.remove("")

    filter_list = ",".join(filter_list)

    parameters = add_arg(parameters, ["-vf", filter_list])

    return parameters

def parse_hdr_params():
    hdr_dict = get_colorspace_params(args.input)
    log.debug(hdr_dict)

    if type(hdr_dict) == "Exception":
        log.error(hdr_dict)
        exit(1)

    colorprim = "color_primaries"
    transfer = "color_transfer"
    colormatrix = "color_space"
    pix_fmt = "pix_fmt"
    master_display = "master-display"
    max_cll = "light-level"

    hdr_params = ["hdr-opt=1:repeat-headers=1"]
    if colorprim in hdr_dict:
        add_arg(hdr_params,f"colorprim={hdr_dict[colorprim]}")

    if transfer in hdr_dict:
        add_arg(hdr_params,f"transfer={hdr_dict[transfer]}")

    if colormatrix in hdr_dict:
        add_arg(hdr_params,f"colormatrix={hdr_dict[colormatrix]}")

    if hdr_dict[master_display] != False:
        carestian_string = f"{master_display}=" \
            f"G({hdr_dict['green_x']},{hdr_dict['green_y']})" \
            f"B({hdr_dict['blue_x']},{hdr_dict['blue_y']})" \
            f"R({hdr_dict['red_x']},{hdr_dict['red_y']})" \
            f"WP({hdr_dict['white_point_x']},{hdr_dict['white_point_y']})" \
            f"L({hdr_dict['max_luminance']},{hdr_dict['min_luminance']})"
        add_arg(hdr_params,carestian_string)

    if hdr_dict[max_cll] != False:
        cll_string=f"max-cll={hdr_dict['max_content']},{hdr_dict['max_average']}"
        add_arg(hdr_params,cll_string)

    param_string = ":".join(hdr_params)

    hdr_settings = { "x265-params" : param_string, pix_fmt: hdr_dict[pix_fmt] }
    return hdr_settings

def parse_resolution(res):
    if res in resolutions:
        res = f"scale={resolutions[res]}"
        return res
    else:
        return f"scale={res}"

    return None

def parse_subtitle_options():
    subs_options = ["subtitles="]
    s = config['subtitles']
    subs_file = s['subtitleExternalFile']
    subs_stream = s['subtitleStream'].lower()
    subs_style = s['subtitleStyle'].lower()

    if is_that_a_no(subs_file):
        log.debug(f"im using the intput files:{args.input}")
        subs_file = args.input

    subs_options.append(subs_file)

    if not is_that_a_no(subs_style):
        subs_options.append(f"style={subs_style}")

    if not is_that_a_no(subs_stream):
        subs_options.append(f"stream_index={subs_stream}")

    subs_string = ":".join(subs_options)
    return subs_string

def parse_audio_options():
    parameters = []
    defaults = dict(codec="aac", bitrate="192k", loudnorm="2pass", channels=2)
    log.info("Parsing audio options")
    a = config['audio']

    #set audio codec
    parameters = add_arg(parameters, ['-c:a'])

    if not is_that_a_no(a['justCopy']):
        parameters = add_arg(parameters, "copy")
        return parameters

    if not is_that_a_no(a['audioCodec']):
        defaults["codec"] = a['audioCodec']

    parameters = add_arg(parameters, defaults["codec"])

    #set audio bitrate
    parameters = add_arg(parameters, "-b:a")

    if not is_that_a_no(a['audioBitrate']):
        defaults["bitrate"] = a['audioBitrate']

    parameters = add_arg(parameters, defaults["bitrate"])

    #set audio channels
    parameters = add_arg(parameters, "-ac")

    if not is_that_a_no(a['audioChannels']):
        defaults["channels"] = a['audioChannels']

    parameters = add_arg(parameters, defaults["channels"])

    if not is_that_a_no(a['loudnorm']):
        parameters = add_arg(parameters, "-af")
        loudnorm_presets = "I=-16:TP=-1.5:LRA=11"
        loudnorm_filter = []
        if a["loudnorm"] == "2pass":
            ln_json = get_loudnorm_params(args.input, loudnorm_presets)

            loudnorm_filter = "".join([
                "loudnorm=", loudnorm_presets,
                ":measured_I=", ln_json["output_i"],
                ":measured_LRA=", ln_json["output_lra"],
                ":measured_TP=", ln_json["output_tp"],
                ":measured_thresh=", ln_json["output_thresh"],
                ":offset=", ln_json["target_offset"],
                ":linear=true"])

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
log.debug(f"got time parameters")

video_params = parse_video_options()
params = add_arg(params, video_params)
show_params(params)
log.debug(f"got video parameters")

audio_params = parse_audio_options()
params = add_arg(params, audio_params)
show_params(params)
log.debug(f"got audio parameters")

params = add_arg(params, args.output)

log.info("All settings parsed. Executing this command:")
log.info(" ".join(params))

returncode, stdout, stderr = run_cmd_get_pipes(params)
log.debug(f"Command ended. $? = {returncode}")
log.debug(f"stderr: {stderr}")
log.debug(f"stdout: {stdout}")

if args.move_old and returncode == 0:
    log.debug("Moving input file")
    final = move_done_file(args.input)
    log.info(final)
