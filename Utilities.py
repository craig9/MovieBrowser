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
        for item in os.listdir(path):
            if ends_with_any(item, exts):
                full = os.path.join(path, item)
                items.append(full)
    except OSError:
        error("Couldn't get files for path '%s', possible a bad directory name. Returning an empty list" % path)
    return items



def get_movie_width(movie):

    return subprocess.check_output(["mediainfo", "--Inform=Video;\"%Width%\"", "%s" % movie])



def get_movie_res(movie):

    tries = 2
    for i in range(tries):
        w = get_movie_width(movie)
        try:
            w = int(w)
            break
        except:
            pass
    else:
        warn("WARNING: for movie %s, mediainfo width not int: '%s' -" % (movie.title, w.strip()))
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
