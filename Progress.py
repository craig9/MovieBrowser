#!/usr/bin/python


import time


from Utilities import *


class Progress:
    
    def __init__(self, log):
        self.start = time.time()
        self.log = log
        self.percent_complete = 0

    def timer(self):
        return time.time() - self.start


    def seconds_remaining(self):

        percent_remaining = 100 - self.percent_complete
        seconds_per_percent_so_far = self.timer() / (self.percent_complete + 0.1)
        seconds_remaining = percent_remaining * seconds_per_percent_so_far
        return seconds_remaining


    def update_log(self, numerator, denominator):
        self.percent_complete = float(numerator) / float(denominator) * 100
        self.log.status("%.1f%% complete, %s remaining" % (self.percent_complete, nice_time(self.seconds_remaining())))
    

    def final_log(self):
        self.log.status("Process took %s" % nice_time(self.timer()))

