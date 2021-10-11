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
parser.add_argument('--config', dest="config", default="settings.conf", type=str, help="config file to read from. Default=settings.conf in single-file mode. settings.conf in source directory if --directory is used.")
parser.add_argument('--input', dest="input", help="Source input video file. Source directory if --directory is used. Will exit with an error if target is not a regular file.", type=str, default="")
parser.add_argument('--output', dest="output", help="Destination file for output. Defualt prepends REENCODED- to input file name in same directory.", type=str, default="REENCODED-")
parser.add_argument('--target', dest="target", help="Destination directory for file output. Default is current working directory.", default="", type=str)
parser.add_argument('--directory', dest="directory", help="Process all files found in a target directory. If --input is omitted, will assume current working directory. If --input specifies a non-directory (either a file or an invalid path), program will exit with an error. Ignores --output flag. Output files will have REENCODED- prepended to the filename if --target is not specified.", default=False, action="store_true")
parser.add_argument('--no-overwrite', dest="safe", help="Prevents overwriting existing files with the output. Conflicts will end the program, or proceed to the next file if working in directory mode.", default=False, action="store_true")

args = parser.parse_args()
print(args)

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.sections()
config.read(args.config)

video = config['video']
print(video['mode'])
