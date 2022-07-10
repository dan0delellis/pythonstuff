#!/usr/bin/env python3
import argparse, logging, logging.handlers, configparser, sys, os.path, time
from process_file import in_hidden_dir, create_path_if_needed, move_file, check_video_stream, feed_to_ffmpeg_front, logger, make_template
#parse arugments
#source dir, output dir, retirement dir, logdir, magic filename

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter('[%(module)s %(levelname)s]: %(message)s')

template_names = ['tv-high', 'tv-normal', 'movie']
template_names_str = ",".join(template_names)

handler.setFormatter(formatter)

log.addHandler(handler)

log.info("Starting program!")

parser = argparse.ArgumentParser()
parser.add_argument(
    '-c', '--configfile', dest="config",  default="reencode.conf", type=str,
    help="Config file to scan for. Files found ONLY in the root dir where this file is found will be processed with this config. Subdirectories are not traversed. Default=reencode.conf "
)

parser.add_argument(
    '-s', '--source-dir', dest="source",  default=".",    type=str,
    help="Source directory root to scan for file accompanying a configured filename"
)

parser.add_argument(
    '-o', '--output-dir', dest="output_dir",  default=False,  type=str,
    help="Destination directory for completed files. Will be created if it doesn't exist. Files will be output in a dir tree matching layout from source dir. Default='.reencode_queue_output' in root of source-dir setting"
)

parser.add_argument(
    '-T', '--test',   dest="testing",    default=False,  action='store_true',
    help="use /usr/bin/echo and just print to stdout what would happen. Also gets set if you use '/usr/bin/echo' as the path for the ffmpeg_front path"
)
parser.add_argument(
    '-d', '--move-done',   dest="move_done",    default=False,  action='store_true',
    help="Move done files to a .done dir in the directory the file exists in. Just passes the --move-done flag to ffmpegfront"
)

parser.add_argument(
    '-l', '--log-dir',    dest="log_dir",     default=False,  type=str,
    help="Directory for log files. Default behavior is to output logs in same dir as source file"
)

parser.add_argument(
    '-k', '--skip-file',  dest="skip_file",  default="all_done.conf", type=str,
    help="Filename to place in root of directory to be skipped. Config file will be renamed to this once all actionable files have been processed."
)

parser.add_argument(
    '-f', '--failed-dir', dest="failed_dir", default=False,   type=str,
    help="Directory to move source files to if re-encoding fails. Defaults to '.reencode-failed' in source dir"
)

parser.add_argument(
    '-m', '--ffront-path', dest="ffront_path", type=str, default="/usr/bin/ffmpeg_front.py",
    help="Executable path for the ffmpeg frontend script. You can test functionality by using '/usr/bin/echo'"
)

parser.add_argument(
    '-p', '--fprobe-path', dest="fprobe_path", type=str, default="/usr/bin/ffprobe",
    help="Executable path to use for ffprobe. use /bin/true for testing on a dir tree without actual video files"
)

parser.add_argument(
    '-t', '--make-template', dest="template", type=str, const="tv-normal", nargs='?',
    help='Make a template file that has pre-configured values for different presets: {template_presets}. Use one of these values with the flag, or you will get a config file that simply copies both the video and audio streams to the target file.'
)

args = parser.parse_args()

if args.template:
    make_template(args.template)
    exit(0)


#if skip-file == config-file there's a logic error and it won't be able to process stuff.
if args.skip_file == args.config:
    log.error("The filename to indicate a directory should be skipped is the same as the name the filename to indicate a directory should be scanned. This isn't gonna work")
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

log.debug(f"root dirs: source: {args.source}, output:{args.output_dir}, failed:{args.failed_dir}, logs: {args.log_dir}. Config file: {args.config}, skip file:{args.skip_file}")

testing = False
if args.testing == True or args.ffront_path == "/usr/bin/echo":
    args.ffront_path = "/usr/bin/echo"
    log.setLevel(logging.DEBUG)
    testing = True

if os.path.abspath(args.source) == os.path.abspath(args.output_dir):
    log.error("The output directory is the same as the source directory. This is a bad idea because you'll just reencode the same set of files forever and fill up your disk")
    os.exit(255)

    #Does the sourcedir exist ? scan source dir : exit 1
if not os.path.isdir(args.source):
    log.error("source dir {} is not a valid path".format(args.source))
    exit(1)

log.debug("herpderp find this string in syslog")
log.debug(f"Source dir: {args.source}")
log.debug(f"Output dir: {args.output_dir}")
log.debug(f"Log dir: {args.log_dir}")
log.debug(f"Failed dir: {args.failed_dir}")

while True:
    log.debug("Starting loop...")
    #Can I find any config files matching the magic filename ? get a list of files in that dir : exit 2
    #Ignore the dir listing with _ because we aren't going to operate on them
        #First, generate a list of all files
    for root, _, files in os.walk(args.source,followlinks=True):
        if args.skip_file in files:
            log.debug(f"Found skip file among files in this dir. Next.")
            continue
        if args.config in files:
        #Does this live in a hidden directory?
            config_file = f"{root}/{args.config}"
            if in_hidden_dir(config_file):
                log.info(f"{config_file} present, but is in a hidden dir. Next")
                continue
            log.debug(f"Operating with config file: {config_file}")
        #Are there any actionable files? Loop through list of actionable files : rename magic file to args.skip_file
            output_root = root.replace(args.source, args.output_dir)
            failed_root = root.replace(args.source, args.failed_dir)
            if not os.path.isdir(output_root):
                log.info(f"Need to create OUTPUT path: {output_root}")
                create_path_if_needed(output_root,template_dir=args.source)
            #For each file, does expected output file already exist ? next : !!FEED FILE TO REENCODER!!
            for in_file in files:
                file_path = f"{root}/{in_file}"
                old_file = f"{root}/.done/{in_file}"
                out_file = f"{output_root}/{in_file}"
                failed_file = f"{failed_root}/{in_file}"
                log_dir = os.path.abspath(f"{args.log_dir}")
                log_file = f"{log_dir}/{in_file}.log"
                log.debug(f"Operating on: {in_file}; Input path: '{file_path}'; Output file: '{out_file}'; failed file: '{failed_file}'; log file: {log_file}")
                log.debug("Testing for expected output file already existing")
                if os.path.isfile(f"{out_file}"):
                    log.info(f"{out_file} already exists. Can't safely continue on this one.")
                    continue
                log.debug(f"Testing {in_file} for video stream")
                if not check_video_stream(file_path,args.fprobe_path):
                    log.debug("This file is not a video file. Next... ")
                    continue
                create_path_if_needed(log_file, make_dir_for_filepath=True)
                log.debug("This is where we'd feed it to ffmpeg_front.pl and hope for the best")

                success = feed_to_ffmpeg_front(
                    CONFIG=config_file,
                    INPUT=file_path,
                    OUTPUT=out_file,
                    LOG_FILE=log_file,
                    move_done=args.move_done,
                    ffront_path=args.ffront_path
                )
                log.info(f"Outcome: succeeded: {success['success']}; stdout: {success['std_out']}; std_err:{success['std_err']}")
                #Did it exit okay ? do nothing because the program handles that already : move file to {failed_dir}
                log.debug(f"Did it exit okay? Moving {in_file} to {old_file} if --old-dir is set")
                if not success['succeeded']:
                    move_file(testing,file_path, failed_file)
                    continue

                if args.move_done:
                    move_file(testing,file_path,old_file)


            completed_config=f"{root}/{args.config}"
            skip_dir_file=f"{root}/{args.skip_file}"
            log.info(f"All files in this dir scanned. Moving {completed_config} to {skip_dir_file}")
            move_file(testing,completed_config, skip_dir_file)
            #end of operations for each file
        #end of instructions if a config file exists in a directory
    #end of files found on os.walk on source directory
    log.info("All files scanned. Sleeping for a while and will restart the loop")
    time.sleep(300)
