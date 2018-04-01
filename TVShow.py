#!/usr/bin/python

import re
from Utilities import *
from TVEpisode import TVEpisode
import os

# TODO Get list of valid video extensions from kodi or VLC source    
# TODO Record a list of extensions we didn't understand. Blacklist some obvious ones from this list (nfo, txt, ...)
video_exts = ['avi', 'mkv', 'mp4', 'm4v', 'mpg', 'mov', 'ogm', 'flv', 'divx']

class TVShow:


    def __init__(self, directory, log):

        self.directory = directory
        self.log = log

        self.title = None
        self.year = None
        self.episodes = []
        self.starred = False
        self.watched = False

        success = self.scan_for_episodes()

        if not success:
            return None

    
    def scan_for_episodes(self):
 
        global video_exts

        self.log.debug("Scanning directory '%s' for TV episodes" % self.directory)
        
        for f in get_files(self.directory, video_exts):
            self.episodes.append(TVEpisode(f))

        self.log.debug("Found %d episodes" % len(self.episodes))

        if len(self.episodes) == 0:
            self.log.warn("No episodes found in %s" % self.directory)
            return False
        else:
            return True



    def __str__(self):

        return ("Directory: %s\nTitle: %s\nYear: %s\nEpisodes: %s\nStarred: %s\nWatched: %s\n" % \
                (self.directory, self.title, self.year, ";".join(self.episides), self.starred, self.watched))



    def is_in_db(self, db):

        matching_records = db.select("SELECT * FROM tv_shows WHERE directory = ?", [self.directory])
    
        if len(matching_records) >= 1:
            self.log.debug("TV Show is in DB")
            return True
        else:
            self.log.debug("TV Show is not in DB")
            return False


    def is_up_to_date(self, db):
        """ We also want to store the date and size of all TV episodes. 
        If there are new files, or the date/size changed, then we are not 
        up to date"""
    
        up_to_date = True

        for episode in self.episodes:
            
            episode.file_date = os.stat(episode.filename).st_mtime
            episode.file_bytes = os.stat(episode.filename).st_size

            sql = "SELECT file_date, file_bytes FROM tv_episodes WHERE filename = ?"

            rows = db.select(sql, [episode.filename])

            if len(rows) != 1:
                self.log.debug("Checking if up to date. Found %d table rows for episode %s" % (len(rows), episode.filename))
                up_to_date = False
            else:
                row = rows[0]

                # FIXME Would be nice to be able to access fields by name, not index
                if row[0] != episode.file_date and row[1] != episode.file_bytes:
                    self.log.debug("Date and/or file size was not correct for episode %s" % episode.filename)
                    up_to_date = False
        
        if up_to_date:
            self.log.debug("%s was up to date" % self.directory)
        else:
            self.log.debug("%s was not up to date" % self.directory)

        return up_to_date



    def read_from_db(self, db):
        """If the show was in the db, and up to date (according to file dates and sizes),
        we end up here, and we use cached data"""

        row = db.select("SELECT title, year, starred FROM tv_shows WHERE directory = ?", [self.directory])[0]

        self.title = row['title']
        self.year = row['year']
        self.starred = row['starred'] 

        for episode in self.episodes:
            e_row = db.select("SELECT filename, title, watched, " + \
                            "file_date, file_bytes " + \
                            "FROM tv_episodes WHERE directory = ? AND filename = ?", \
                            [self.directory, episode.filename])[0]

            episode.title = e_row['title']
            episode.watched = e_row['watched']
            episode.file_date = e_row['file_date']
            episode.file_bytes = e_row['file_bytes']



    def read_from_disk(self):
        """Unless the show was in the db and up to date (according to episode 
        dates and sizes) - we will re-read all info from disk into memory"""

        self.log.debug("Reading from disk")

        last_segment = os.path.split(self.directory)[-1]
        match = re.search("(.*?)\s*?\((\d{4})\)", last_segment)
        if match:
            title = match.group(1)
            year = match.group(2)
        else:
            self.log.error("Could not determine title and year in '%s'" % last_segment)
            title = last_segment
            year = "0"

        self.title = title
        self.year = year
        self.starred = False

        for e in self.episodes:
            self.log.debug("Reading episode from disk: %s" % e.filename)
            short_filename = os.path.split(e.filename)[-1]
            e.title = short_filename.rsplit('.', 1)[0]
            e.watched = False
            e.file_date = os.stat(e.filename).st_mtime
            e.file_bytes = os.stat(e.filename).st_size


    def update_db(self, db):

        rows = db.select("SELECT * FROM tv_shows WHERE directory = ?", [self.directory])
        
        if len(rows) == 0:
            self.log.debug("Inserting show %s" % self.title)
            db.exec_sql("INSERT INTO tv_shows (directory, title, year, " + \
                        "starred) VALUES (?, ?, ?, ?)", [self.directory, \
                        self.title, self.year, self.starred])

        for e in self.episodes:
            rows = db.select("SELECT * FROM tv_episodes WHERE directory = ? " + \
                            "AND filename = ?", [self.directory, e.filename])

            if len(rows) == 0:
                db.exec_sql("INSERT INTO tv_episodes(directory, filename, title, " + \
                            "file_date, file_bytes, watched) VALUES " + \
                            "(?, ?, ?, ?, ?, ?)", \
                            [self.directory, e.filename, e.title, \
                            e.file_date, e.file_bytes, False])
            elif len(rows) == 1:
                # Purposely don't update 'watched' status
                db.exec_sql("UPDATE tv_episodes SET title = ?, " + \
                    "file_date = ?, file_bytes = ? WHERE directory = ? AND " + \
                    "filename = ?", [e.title, e.file_date, \
                    e.file_bytes, self.directory, e.filename])
            else:
                self.log.error("More than 1 copy of %s %s existed in db" % [self.directory, e.filename])
        

            self.log.debug ("Updating db: %s - %s" % (self.directory, e.filename))


