#!/usr/bin/env python3
from columnar import columnar
#pip install columnar

def conf_help(name):
    video_msg = [
        ["Supported options:", "","",""],
        ["[video]","","",""],
        ["name", "values", "description", "default"],
        ["rasPiHardwareEncode", "True/False",  "Will use functions for a raspberry pi 4 video chip. Super esoteric and not really worth it.","false"],
        ["justCopy", "True/False", "Just copy video stream, no filters/subtitles/resizing.","False"],
        ["videoCodec","string","Video codec to encode with. `ffmpeg -encoders` will list available formats", "libx265"],
        ["videoProfile","string","Profile to use while encoding. Different codecs have different profiles.","high10"],
        ["preset","string","speed at which to encode. slower=better quality typically","slow"],
        ["resolution","string","Resize video to given res, in width:height. Also accepts:\n480p=640:480,\n720p=1280:720,\n1080p=1920:1080\n4k=3840:2160",""],
        ["mode", "CRF/CBR", "Use Constant Rate Factor or Constant Bit Rate.","Default: CRF"],
        ["quality", "number", "Quality factor to target in CRF mode.","21"],
        ["videoBitrate","<number><M/K>","target average video bitrate","2M"],
        ["videoMinrate","<number><M/K>","target minimum video bitrate","1M"],
        ["videoMaxrate","<number><M/K>","target maximum video bitrate","4M"],
        ["videoBufSize","<number><M/K>","video buffer size","6M"]
    ]

    audio_msg = [
        ["justCopy","True/False","Just copy the audio streams","False"],
        ["audioCodec","string","Codec to use for audio encoding.\n`ffmpeg -encoders` will list available codecs.","aac"],
        ["audioChannels","number","Number of audio channels to mux to","2"],
        ["audioBitrate","<number><M/K>","Bitrate to use for audio encoding","200K"],
        ["loudnorm", "True/False/2pass", "Use loudnorm to normalize audio levels","2pass"]
    ]

    subs_msg = [
        ["burnInSubtitles","True/False","Hardcode subtitle files","False"],
        ["subtitleFile","filename","File to use for subs. If the subs are in the video file, you can specify the video file and the sub index","<video file name>:si=1"],
        ["subtitleStyle","string","Style settings for subs. Google it.","<none>"],
    ]

    time_msg = [
        ["introSkipSeconds","number","Number of seconds to skip at the start of the file","0"],
        ["totalTimeSeconds","number","total number of seconds to have in the video file.\n0 is counted as <input length - skipped seconds>","0"],
    ]

    msg = {
        "video": video_msg,
        "audio": audio_msg,
        "subs": subs_msg,
        "time": time_msg
    }
    return msg[name]


names = ["video","audio","subs","time"]

for name in names:
    table = columnar(conf_help(name), no_borders=False)
    print(table)
