#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess


def ends_with_any(needle, endings):

    for ending in endings:
        if needle.endswith(ending):
            return True
    return False



def get_subdirs(movies_root):

    items = []
    for subdir in sorted(os.listdir(movies_root)):
        full_subdir = os.path.join(movies_root, subdir)
        if os.path.isdir(full_subdir):
            items.append(full_subdir)
    return items



def get_files(path, exts):

    items = []
    # Ensure the directory will list its contents (directories with colons in the name don't)
    try:
        #for item in os.listdir(path):
        for item in get_all_files(path):
            if ends_with_any(item, exts):
                full = os.path.join(path, item)
                items.append(full)
    except OSError:
        error("Couldn't get files for path '%s', possible a bad directory name. Returning an empty list" % path)
    return items



def get_video_width(video):

    return subprocess.check_output(["mediainfo", "--Inform=Video;\"%Width%\"", "%s" % video])



def get_video_res(video):

    tries = 2
    for i in range(tries):
        w = get_video_width(video)
        try:
            w = int(w)
            break
        except:
            pass
    else:
        print("WARNING: for video %s, mediainfo width not int: '%s' -" % (video, w.strip()))
        return "?"

    if w <= 960:
        return "SD"
    elif w <= 1280:
        return "720p"
    else:
        return "1080p"



def nice_time(seconds):

    if seconds > 60 * 60: # Hours
        return "%.1f hours" % (seconds / float(60 * 60))
    elif seconds > 60:
        return "%.1f minutes" % (seconds / float(60))
    else:
        return "%d seconds" % seconds

def get_all_files(folder):
    for root, subdirs, files in os.walk(folder):
        subdirs.sort()
        for f in sorted(files):
            yield(os.path.join(root, f))

def get_folders(root):
    for folder in sorted(os.listdir(root)):
        full_folder = os.path.join(root, folder)
        if os.path.isdir(full_folder):
            yield full_folder

def is_video(filename):
    movie_suffixes = ['avi', 'm4v', 'mkv', 'mp4', 'mov', 'divx', 'fanart.jpg', 'mpg', 'flv', 'ogm']

    parts = filename.rsplit(".", 1)

    return len(parts) == 2 and parts[1] in movie_suffixes

def get_videos(folder):
    for f in get_all_files(folder):
        if is_video(f):
            yield f
