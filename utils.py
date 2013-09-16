'''
Created on Jan 28, 2011

@author: yangwookkang
'''

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
    
class ConsoleAndFileLogger:
    def __init__(self, sessionid):
        self.sessionid = sessionid
        self.logfile   = open("./log/log_" + sessionid+".txt", "w")

    def log(self, msg):
        print msg
        print >> self.logfile, msg
        self.logfile.flush()
    
    def logtofile(self, msg):
        print >> self.logfile, msg
        self.logfile.flush()