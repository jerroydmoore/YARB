'''
Created on Jan 28, 2011

@author: yangwookkang
'''

import pickle 
import os
import sys

class LocalDBWrapper:
	def __init__(self):
		self.pretable = {}
		self.setWValues(0.3, 1.0, 1.0)
		self.setOutputType(1)
	
	def load_preference(self, username):
		try: 
			savepath = os.path.normpath(os.path.join(sys.path[0], "./localdb/" + username + ".prep"))
			
			logfile   = open(savepath, "rb")
			self.pretable = pickle.load(logfile)
			logfile.close()
			return 1
		except IOError:
			return 0
	
	def store_preference(self, username):
		savepath = os.path.normpath(os.path.join(sys.path[0], "./localdb/" + username + ".prep"))
		
		output = open(savepath, 'wb')
		pickle.dump(self.pretable, output)
		output.close()
	
	def get_preference(self):
		return self.pretable
	
	def add_preference(self, type, value, rating):
		self.pretable[value] = type + ":" + str(rating)
		
	def setOutputType(self, count):
		self.pretable["output"] = count

	def setWValues(self, count1, count2, count3):
		self.pretable["w1"] = count1
		self.pretable["w2"] = count2
		self.pretable["w3"] = count3
		
	def getOutputType(self):
		try:
			return self.pretable["output"]
		except KeyError:
			return 1
	def getW1(self):
		try:
			return self.pretable["w1"]
		except KeyError:
			return 1
	def getW2(self):
		try:
			return self.pretable["w2"]
		except KeyError:
			return 1
	def getW3(self):
		try:
			return self.pretable["w3"]
		except KeyError:
			return 1
''' 

# localdbwrapper test

l = LocalDBWrapper()

# store
l.add_preference("director", "Steven Spielberg", 5) 
l.add_preference("person", "Julia Roberts", 4)
l.add_preference("movie", "The lord of the rings", 4)
l.store_preference("ywkang")

# load

l.load_preference("ywkang")
print l.get_preference()

'''