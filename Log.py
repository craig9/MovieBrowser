#!/usr/bin/python

import os



class Log:

    def __init__(self, log_file_path, log_level_file = 4, log_level_screen = 4):
        # 1 = error, 2 = warnings, 3 = status, 4 = debug
        self.log_level_file = log_level_file
        self.log_level_screen = log_level_screen
        self.log_file = os.path.join(log_file_path, "movie_browser_log.txt")

        self.log("INFORMATION: New log file session", 4)



    def log(self, msg, log_level = 1):

        # TODO add dates and times automatically

        if self.log_level_screen >= log_level:
            print(msg)

        if self.log_level_file >= log_level:
            fh = open(self.log_file, "a+")
            fh.write(msg + "\n")
            fh.close()


    def error(self, msg):
        self.log("ERROR: %s" % msg, 1)


    def warn(self, msg):
        self.log("WARN: %s" % msg, 2)


    def status(self, msg):
        self.log("STATUS: %s" % msg, 3)


    def debug(self, msg):
        self.log("DEBUG: %s" % msg, 4)

