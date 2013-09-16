'''
Created on Feb 2, 2011

@author: yangwookkang
'''

class Movie(object):
   
    def __init__(self, title, year, score = 0):
        self.title = title
        self.year = year
        self.score = score
        pass
    
    def get_score(self):
        return self.score
    
    def get_title(self):
        return self.title
    
    def get_year(self):
        return self.year
        