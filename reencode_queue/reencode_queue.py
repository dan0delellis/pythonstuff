#!/usr/bin/env python3
import argparse, logging, configparser, sys, os.path
#parse arugments
#source dir, output dir, retirement dir, logdir, magic filename

parser = argparse.ArgumentParser()
parser.add_argument(
    '--configfile',
    dest="config",
    default="reencode.conf",
    type=str,
    help="config file to scan for. ALL files found the root dir where this file is found will be processed with this config. Files deeper in the tree will be operated on first, so placing a deeper config file will override one closer to the root Default=reencode.conf "
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
    dest="output",
    default=False,
    type=str,
    help="Destination directory for completed files. Will be created if it doesn't exist. Files will be output in a dir tree matching layout from source dir. Default='done' in root of sourse-dir setting"
)

parser.add_argument(
    '--old-dir',
    dest="old_files",
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


#flow:
    #parse options
args = parser.parse_args()
    #Does the sourcedir exist ? scan source dir : exit 1
if not os.path.isdir(args.source):
    print("source dir {} is not a valid path".format(args.source))
    exit(1)
    #Can I find any config files matching the magic filename ? get a list of files in that dir root from the max depth : exit 2
        #This is more complicated than I thought it would be
        #First, generate a list of all
for root, dirs, files in os.walk(args.source):
    if args.skip_file in files:
        continue
    #Are there any actionable files? Loop through list of actionable files : rename magic file to args.skip_file
        #For each file, does expected output file already exist ? next : !!FEED FILE TO REENCODER!!
            #Did it exit okay ? Move file to {old_dir} : move file to {failed_dir}
