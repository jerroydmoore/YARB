'''
Agent 

Created on Jan 28, 2011

@author: yangwookkang
'''

import time
import utils
import sys
from nlu.NLparser import NLparser
from nlg.NLgenerator import NLgenerator
from dm.dialogmanager import DialogManager
from datetime import date
from dm.imdb_wrapper import IMDBWrapper
from dm.localdb_wrapper import LocalDBWrapper
from nlu.entity import EntitySet

class Agent:
	def __init__(self, verbose = False):
		# load modules 
		#     NLU, DB connection test
		
		
		self.nlu = NLparser(verbose)
		
		# verbose true for DM and NLG
		verbose = True
		
		self.dm  = DialogManager(verbose)
		self.nlg = NLgenerator(verbose)
		self.sessionid = date.strftime(date.today(),"%y%m%d") + "_" + time.strftime("%H%M%S")
		self.logger = utils.ConsoleAndFileLogger(self.sessionid)
	
	
	def run(self):
		self.logger.log("Hello. I am YARB (Yet Another Recommendation Bot).")
		self.logger.log("Please tell me your name.")
		usermsg = raw_input("> ")
		self.logger.logtofile("> " + usermsg)
		if (self.dm.processUserName(usermsg) == 1):
			self.logger.log("Welcome back, " + usermsg + ".")
		else: 
			self.logger.log("Nice to meet you, " + usermsg + ".")
		self.logger.log("If you'd like a recommendation, please tell\nme about what you like or dislike.")
		
		self.dm.loadOptions()

		while not self.dm.sessionclosed():
			usermsg = raw_input("> ")
			self.logger.logtofile("> " + usermsg)
			
			if usermsg == "":
				continue

			nluoutput = self.nlu.process(usermsg)            # NLU
			
			for output in nluoutput:
				dmoutput  = self.dm.process(output)           # DM
			#dmoutput  = self.dm.process(nluoutput)
				
			response  = self.nlg.process(dmoutput)           # NLG
			
			self.logger.log(response)
			
		self.dm.saveUserPreferences()
		self.logger.log("Session closed [id = {0:s}].".format(self.sessionid))

	def test(self, inputfilename):
		print 'reading: ' + inputfilename
		infile = open(inputfilename, 'r')
		
		num = 1
		breakpoint = 29
		
		print 'processing... classifier: trivia'
		for line in infile:
			# NLU process
			input = line.strip()
				#print input
			nluoutput = self.nlu.process(input)            # NLU
			
			#if num != breakpoint and nluoutput.get_classifier() != "userPreference":
			#	num = num + 1
			#	continue
				
			#if breakpoint == num:
				#print str(num) + ". " + line.replace('\\','') + " --> " + nluoutput.get_classifier() + " , [", nluoutput.tostr_entities(), "]"
					
			#if nluoutput.get_classifier() == "trivia":
			print str(num) + ". " + input
			dmoutput = self.dm.process(nluoutput)
			msg = self.nlg.process(dmoutput)
			print "> " + msg
			print 
		
			num = num + 1

def test_db():
	IMDBWrapper()
	pass

# main function
if __name__ == '__main__':
	#test_db()
	#Agent().test("./corpus1.txt")
	Agent().run()
	"""
		
	# imdb test
	
	localdb = LocalDBWrapper()
	localdb.load_preference("ywkang")
	#localdb.add_preference("genre", "Comedy", 4)
	print localdb.get_preference()
	
	
	db = IMDBWrapper()
	
	entities = EntitySet("dummy")
	
	db.get_recommendation(entities, localdb.get_preference())
	"""


