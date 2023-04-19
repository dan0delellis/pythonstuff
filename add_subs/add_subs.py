#!/usr/bin/python3
import os.path as path
from os import listdir,walk
import argparse, hashlib,subprocess

minsize = 10 * 1024 * 1024
ffmpeg_bin = "/usr/bin/ffmpeg"
mv_bin = "/usr/bin/mv"
tar_bin = "/usr/bin/tar"
rm_bin = "/usr/bin/rm"
echo_bin = "/usr/bin/echo"

parser = argparse.ArgumentParser()
parser.add_argument(
    '--lookdir', '-d',
    dest="epdir",
    default=".",
    type=str,
    help="Directory to look for episodes. Default= ."
)
parser.add_argument(
    '--subs', '-s',
    dest="subpath",
    default="Subs",
    type=str,
    help="Directory name with subtitle files. Default=./Subs"
)
parser.add_argument(
    '--test', '-t',
    dest="dry_run",
    default=False,
    action='store_true',
    help="Don't actually run commands, just process the files"
)
args = parser.parse_args()

def run_cmd(cmd):
    p = subprocess.Popen(cmd.split())
    p.wait()
    return p

class Episode:
    def __init__(self, fname, subsdir):
        self.fpath =  path.realpath(fname)
        self.ep_name,ext  = path.splitext(path.basename(fname))
        self.tempfile = "".join(("/tmp/",hashlib.md5(self.fpath.encode('utf-8')).hexdigest(),ext))
        subsroot = ""
        if path.isdir(subsdir):
            subsroot = path.realpath(subsdir)
        else:
            subsroot = path.join(path.dirname(self.fpath),subsdir)
        self.real_subs = path.join(subsroot,self.ep_name)
        print(f"****\n{self.real_subs}\n***")
        if not path.isdir(self.real_subs):
            self.cmd = self.done_cmd = self.tar_subs = f"{echo_bin} \"'{self.real_subs}' is not a directory\""
            return
        self.subs_files  = []
        self.cmd = f"{ffmpeg_bin} -hide_banner -i {self.fpath}"
        stream = 1
        for i in listdir(self.real_subs):
            sub_path = path.join(self.real_subs,i)
            self.subs_files.append(sub_path)
            self.cmd += f" -i {sub_path}"
            stream += 1
        if stream==1:
            self.cmd = self.done_cmd = self.tar_subs = f"{echo_bin} \"No subtitles found for '{self.ep_name}'\""
            return
        for i in range(0,stream):
            self.cmd += f" -map {i}"
        self.cmd += f" -c copy -c:s mov_text {self.tempfile}"
        self.done_cmd = f"{mv_bin} {self.tempfile} {self.fpath}"
        self.tar_subs = f"{tar_bin} -C {subsroot} -cf {self.real_subs}.tar {self.ep_name} --remove-files"

print("listing files")
for files in listdir(args.epdir):
    actual_ep = path.join(args.epdir,files)
    if path.getsize(actual_ep) < minsize:
        print(f"{actual_ep} is too small. next")
        continue
    t = Episode(actual_ep,args.subpath)
    print(t.cmd)
    print(t.done_cmd)
    print(t.tar_subs)
    if args.dry_run:
        continue
    p = run_cmd(t.cmd)
    if p.returncode != 0:
        print(p.stderr)
        continue
    p = run_cmd(t.done_cmd)
    if p.returncode > 0:
        print(err)
        continue
    p = run_cmd(t.tar_subs)
    if p.returncode > 0:
        print(err)
        continue
