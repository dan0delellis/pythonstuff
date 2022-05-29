#!/usr/bin/env python3
import sys
import subprocess
import re
import os, os.path
import shutil

def in_hidden_dir(path):
    hidden = False
    file_realpath = os.path.abspath(path)
    file_location = os.path.dirname(file_realpath)
    dir_tree = file_location.split("/")
    for leaf in dir_tree:
        hidden = re.search("^\..+$", leaf)
        if hidden:
            return hidden
    return hidden

#def create_path_if_needed(path):

