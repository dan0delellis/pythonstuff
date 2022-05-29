#!/usr/bin/env python3
import argparse, logging, configparser, sys, os.path
from process_file import in_hidden_dir
#parse arugments
#source dir, output dir, retirement dir, logdir, magic filename

parser = argparse.ArgumentParser()
parser.add_argument(
    '--configfile',
    dest="config",
    default="reencode.conf",
    type=str,
    help="Config file to scan for. Files found ONLY in the root dir where this file is found will be processed with this config. Subdirectories are not traversed. Default=reencode.conf "
)

parser.add_argument(
    '--source-dir',
    dest="source",
    default=".",
    type=str,
    help="Source directory root to scan for file accompanying a configured filename"
)

parser.add_argument(
    '--output-dir',
    dest="output_dir",
    default=False,
    type=str,
    help="Destination directory for completed files. Will be created if it doesn't exist. Files will be output in a dir tree matching layout from source dir. Default='done' in root of sourse-dir setting"
)

parser.add_argument(
    '--old-dir',
    dest="old_dir",
    default=False,
    type=str,
    help="Destination directory for original files that have been successfully reencoded. Default is to leave files in place."
)

parser.add_argument(
    '--log-dir',
    dest="log_dir",
    default=False,
    type=str,
    help="Directory for log files. Default behavior is to output logs in same dir as source file"
)

parser.add_argument(
    '--skip-file',
    dest="skip_file",
    type=str,
    default="all_done.conf",
    help="Filename to place in root of directory to be skipped. Config file will be renamed to this once all actionable files have been processed."
)

parser.add_argument(
    '--failed-dir',
    dest="failed_dir",
    type=str,
    default=False,
    help="Directory to move source files to if re-encoding fails. Defaults to '.reencode-failed' in source dir"
)

args = parser.parse_args()

#flow:
    #parse options
    #check for defaults that are set to False and set them because I forget why I did that
if args.failed_dir == False:
    args.failed_dir = f"{args.source}/.reencode-failed/"
if args.log_dir == False:
    args.log_dir = args.source
#if args.old_dir == False:
    #Do nothing because default behavior is to keep files in place
if args.output_dir == False:
    args.output_dir = f"{args.source}/.done/"

    #Does the sourcedir exist ? scan source dir : exit 1
if not os.path.isdir(args.source):
    print("source dir {} is not a valid path".format(args.source))
    exit(1)
    #Can I find any config files matching the magic filename ? get a list of files in that dir : exit 2
        #First, generate a list of all files
#Ignore the dir listing with _ because we aren't going to operate on them
for root, _, files in os.walk(args.source):
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
        #For each file, does expected output file already exist ? next : !!FEED FILE TO REENCODER!!
        for in_file in files:
            file_path = f"{root}/{in_file}"
            out_file = f"{output_root}/{in_file}"
            old_file = f"{args.old_dir}/{in_file}"
            print(f"Operating on: {in_file}")
            print(f"\tInput path: '{file_path}'; Output file: '{out_file}'; Old file: '{old_file}'")
            print("\tDoes the expected output file already exist?")
            if os.path.isfile(f"{out_file}"):
                print(f"\t{in_file} already exists.")
                print(f"\tmoving {in_file} to {old_file}. Next...")
                continue
            print("\tThis is where we'd test if it has a video stream")
            print("\tThis is where we'd feed it to ffmpeg_front.pl and hope for the best")
            print(f"\tDid it exit okay? Moving {in_file} to {old_file} if --old-dir is set to a path")
            #Did it exit okay ? Move file to {old_dir} : move file to {failed_dir}
        print(f"Moving {root}/{args.config} to {root}/{args.skip_file}")
