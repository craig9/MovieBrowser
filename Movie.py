#!/usr/bin/python


import xml.etree.ElementTree as ET


from Utilities import *


# TODO Get list of valid video extensions from kodi or VLC source    
# TODO Record a list of extensions we didn't understand. Blacklist some obvious ones from this list (nfo, txt, ...)
movie_exts = ['avi', 'mkv', 'mp4', 'm4v', 'mpg', 'mov', 'ogm', 'flv', 'divx']

class Movie:


    def __init__(self, directory, log):

        self.directory = directory
        self.log = log

        self.title = None
        self.year = None
        self.rating = None
        self.resolution = None
        self.nfo_files = []
        self.movie_files = []
        self.genres = []
        self.runtime = None
        self.filesize = None
        self.nfo_date = None
        self.nfo_bytes = None
        self.movie_date = None
        self.movie_bytes = None


        nfo_success = self.scan_for_nfo_files()
        movies_success = self.scan_for_movie_files()

        if not nfo_success or not movies_success:
            return None



    def scan_for_nfo_files(self):

        self.log.debug("Scanning directory '%s' for NFO files" % self.directory)

        self.nfo_files = get_files(self.directory, ['.nfo']) 

        if len(self.nfo_files) == 0:
            self.log.warn("Missing NFO file in %s" % self.directory)
            return False

        if len(self.nfo_files) > 1:
            self.log.warn("Multiple NFO files found in %s, only using first one found" % self.directory)
        
        return True


    
    def scan_for_movie_files(self):
 
        global movie_exts

        self.log.debug("Scanning directory '%s' for movie files" % self.directory)
        
        self.movie_files = get_files(self.directory, movie_exts)

        if len(self.movie_files) == 0:
            self.log.warn("Missing movie file in %s" % self.directory)
            return False

        return True



    def __str__(self):

        return ("Dir: %s\nNFOs: %s\nFilenames: %s\nTitle: %s\nYear: %s\nRating: %s\nResolution: %s\nGenres: %s\nFilesize: %s\nRuntime: %s" % \
               (self.directory, ";".join(self.nfo_files), ";".join(self.movie_files), self.title, self.year, \
                self.rating, self.resolution, self.genres, self.filesize, self.runtime))


    def is_in_db(self, db):

        
        matching_records = db.select("SELECT * FROM movies WHERE filenames = ? and nfo = ?", (";".join(self.movie_files), self.nfo_files[0]))
    
        if len(matching_records) >= 1:
            self.log.debug("Movie is in DB")
            return True
        else:
            self.log.debug("Movie is not in DB")
            return False


    def is_up_to_date(self, db):
        """We store the date and size of both movie and nfo files. If the current dates/sizes differ from
        the cached dates/sizes, then the file is not up to date."""

        live_nfo_date = os.stat(self.nfo_files[0]).st_mtime
        live_movie_date = os.stat(self.movie_files[0]).st_mtime
        live_nfo_bytes = os.stat(self.nfo_files[0]).st_size
        live_movie_bytes = os.stat(self.movie_files[0]).st_size

        sql = "SELECT nfo_date, nfo_bytes, movie_date, movie_bytes FROM movies WHERE filenames = ?"
        filenames = ";".join(self.movie_files)
        row = db.select(sql, [filenames])[0] # FIXME Would be nice to be able to access fields by name, not index
        
        if row[0] == live_nfo_date and \
        row[1] == live_nfo_bytes and \
        row[2] == live_movie_date and \
        row[3] == live_movie_bytes:
            self.log.debug("%s was up to date" % self.movie_files)
            return True

        self.log.debug("%s was not up to date" % self.movie_files)
        return False

    def read_from_db(self, db):
        
        sql = "SELECT nfo, title, year, rating, resolution, genres, filesize, runtime, nfo_date, nfo_bytes, movie_date, movie_bytes FROM movies WHERE filenames = ?"
        filenames = ";".join(self.movie_files)
        row = db.select(sql, [filenames])[0]

        self.nfo = row[0] # FIXME Again, need to look at accessing fields by name, not position. Soon!
        self.title = row[1]
        self.year = row[2]
        self.rating = row[3]
        self.resolution = row[4]
        self.genres = row[5]
        self.filesize = row[6]
        self.runtime = row[7]
        self.nfo_date = row[8]
        self.nfo_bytes = row[9]
        self.movie_date = row[10]
        self.movie_bytes = row[11]
        
    
    def read_from_disk(self):

        tree = ET.parse(self.nfo_files[0])
        root = tree.getroot()
        self.title = root.find('title').text.encode("utf-8")
        self.rating = "%.1f" % float(root.find('rating').text.encode("utf-8"))
        try:
            self.year = root.find('year').text.encode("utf-8")
        except AttributeError:
            self.log.error("Could not find year element in NFO file '%s'" % self.nfo_files[0])
            self.year = 0

        # Genres
        for genre in root.findall('genre'):
            if genre.text is None:
                continue
            genre = genre.text.encode("utf-8") 
            nested_genres = genre.split("/")
            for nested_genre in nested_genres:
                nested_genre = nested_genre.strip()
                if nested_genre not in self.genres:
                    self.genres.append(nested_genre)

        #self.resolution = "?"
        filename = os.path.join(self.directory, self.movie_files[0])
        self.resolution = get_movie_res(filename)

        runtime = root.find('runtime')
        if runtime is not None:
            self.runtime = runtime.text.encode("utf-8")
        else:
            self.runtime = 0
        
        filesize = 0
        for movie_file in self.movie_files:
            filesize += os.stat(movie_file).st_size / 2**20
        self.filesize = "%d MB" % filesize

        self.nfo_date = os.stat(self.nfo_files[0]).st_mtime
        self.movie_date = os.stat(self.movie_files[0]).st_mtime
        self.nfo_bytes = os.stat(self.nfo_files[0]).st_size # FIXME Possibly need to concatenate the file sizes for all four attributes
        self.movie_bytes = os.stat(self.movie_files[0]).st_size

    def delete_from_db(self, db):
        filenames = ";".join(self.movie_files)
        db.exec_sql("DELETE FROM movies WHERE filenames = ?", [filenames])

    def insert_to_db(self, db):
        try:
            filenames = ";".join(self.movie_files)
            if len(self.nfo_files) > 0:
                nfo = self.nfo_files[0]
            else:
                nfo = ""
            title = self.title
            year = self.year
            rating = self.rating
            res = self.resolution
            genres = ";".join(self.genres)
            filesize = self.filesize
            runtime = self.runtime
            nfo_date = self.nfo_date
            nfo_bytes = self.nfo_bytes
            movie_date = self.movie_date
            movie_bytes = self.movie_bytes

        except:
            self.log.error("Something went wrong, couldn't add this to database: %s" % movie)
            return

        sql = "INSERT INTO movies (filenames, nfo, title, year, rating, resolution, genres, filesize, runtime, nfo_date, nfo_bytes, movie_date, movie_bytes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        db.exec_sql(sql, (filenames, nfo, title, year, rating, res, genres, filesize, runtime, nfo_date, nfo_bytes, movie_date, movie_bytes))

