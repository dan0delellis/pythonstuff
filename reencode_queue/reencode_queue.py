#!/usr/bin/env python3
import argparse, logging, configparser, sys, os.path
from process_file import in_hidden_dir, create_path_if_needed, move_file, check_video_stream, feed_to_ffmpeg_front
#parse arugments
#source dir, output dir, retirement dir, logdir, magic filename

parser = argparse.ArgumentParser()
parser.add_argument(
    '--configfile', dest="config",  default="reencode.conf", type=str,
    help="Config file to scan for. Files found ONLY in the root dir where this file is found will be processed with this config. Subdirectories are not traversed. Default=reencode.conf "
)

parser.add_argument(
    '--source-dir', dest="source",  default=".",    type=str,
    help="Source directory root to scan for file accompanying a configured filename"
)

parser.add_argument(
    '--output-dir', dest="output_dir",  default=False,  type=str,
    help="Destination directory for completed files. Will be created if it doesn't exist. Files will be output in a dir tree matching layout from source dir. Default='.reencode_queue_output' in root of source-dir setting"
)

parser.add_argument(
    '--move-old',   dest="move_old",    default=False,  type=bool,
    help="Move done files to a .done dir in the directory the file exists in. Just passes the --move-done flag to ffmpegfront"
)

parser.add_argument(
    '--log-dir',    dest="log_dir",     default=False,  type=str,
    help="Directory for log files. Default behavior is to output logs in same dir as source file"
)

parser.add_argument(
    '--skip-file',  dest="skip_file",  default="all_done.conf", type=str,
    help="Filename to place in root of directory to be skipped. Config file will be renamed to this once all actionable files have been processed."
)

parser.add_argument(
    '--failed-dir', dest="failed_dir", default=False,   type=str,
    help="Directory to move source files to if re-encoding fails. Defaults to '.reencode-failed' in source dir"
)

parser.add_argument(
    '--ffront-path', dest="ffront_path", type=str, default="/usr/bin/ffmpeg_front.py",
    help="Executable path for the ffmpeg frontend script. You can test functionality by using '/usr/bin/echo'"
)

parser.add_argument(
    '--fprobe-path', dest="fprobe_path", type=str, default="/usr/bin/ffprobe",
    help="Executable path to use for ffprobe. use /bin/true for testing on a dir tree without actual video files"
)

args = parser.parse_args()

#if skip-file == config-file there's a logic error and it won't be able to process stuff.
if args.skip_file == args.config:
    print("The filename to indicate a directory should be skipped is the same as the name the filename to indicate a directory should be scanned. This isn't gonna work")
    exit(255)

#flow:
    #parse options
    #check for defaults that are set to False and set them because I forget why I did that
if args.failed_dir == False:
    args.failed_dir = f"{args.source}/.reencode-failed/"
if args.log_dir == False:
    args.log_dir = args.source
if args.output_dir == False:
    args.output_dir = f"{args.source}/.reencode_queue_completed/"

    #Does the sourcedir exist ? scan source dir : exit 1
if not os.path.isdir(args.source):
    print("source dir {} is not a valid path".format(args.source))
    exit(1)
    #Can I find any config files matching the magic filename ? get a list of files in that dir : exit 2
        #First, generate a list of all files
#Ignore the dir listing with _ because we aren't going to operate on them
for root, _, files in os.walk(args.source,followlinks=True):
    if args.skip_file in files:
        continue
    if args.config in files:
    #Does this live in a hidden directory?
        config_file = f"{root}/{args.config}"
        if in_hidden_dir(config_file):
            print(f"{config_file} present, but is in a hidden dir")
            continue
    #Are there any actionable files? Loop through list of actionable files : rename magic file to args.skip_file
        output_root = root.replace(args.source, args.output_dir)
        if not os.path.isdir(output_root):
            print(f"Need to create path: {output_root}")
            create_path_if_needed(output_root,template_dir=args.source)
        #For each file, does expected output file already exist ? next : !!FEED FILE TO REENCODER!!
        for in_file in files:
            file_path = f"{root}/{in_file}"
            old_file = f"{root}/.done/{in_file}"
            out_file = f"{output_root}/{in_file}"
            print(f"Operating on: {in_file}")
            print(f"\tInput path: '{file_path}'; Output file: '{out_file}'")
            print("\tDoes the expected output file already exist?")
            if os.path.isfile(f"{out_file}"):
                print(f"\t{out_file} already exists. Can't safely continue on this one.")
                continue
            print("\tThis is where we'd test if it has a video stream")
            if not check_video_stream(in_file,args.fprobe_path):
                print("\tThis file is not a video file. Next... ")
                continue
            print(f"\tSet log file location:")
            log_dir = os.path.dirname(f"{args.log_dir}/{file_path}")
            log_file = f"{log_dir}/{file_path}.log"
            create_path_if_needed(log_file, make_dir_for_filepath=True)
            print("\tThis is where we'd feed it to ffmpeg_front.pl and hope for the best")

            success = feed_to_ffmpeg_front(
                CONFIG=config_file,
                INPUT=file_path,
                OUTPUT=out_file,
                LOG_FILE=log_file,
                move_done=args.move_old,
                ffront_path=args.ffront_path
            )

            #Did it exit okay ? do nothing because the program handles that already : move file to {failed_dir}
            print(f"\tDid it exit okay? Moving {in_file} to {old_file} if --old-dir is set")
            if not success:
                print(f"\tSet the failed reencode location:")
                failed_dir=f"{args.failed_dir}/{file_path}"
                failed_file = f"{failed_dir}/{file_path}"
                move_file(file_path, failed_file)

        completed_config=f"{root}/{args.config}"
        skip_dir_file=f"{root}/{args.skip_file}"
        print(f"Moving {completed_config} to {skip_dir_file}")
        move_file(completed_config, skip_dir_file)
