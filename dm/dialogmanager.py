'''
Created on Jan 28, 2011

@author: yangwookkang
'''

from dmoutput import DmOutput
from dmoutput import ListItem
import imdb_wrapper
from localdb_wrapper import LocalDBWrapper
import math
import random

class DialogManager:
	INIT, PAGING, ASKINGFORLIKES, ASKINGFORREC, QUIZZING = range(5)
	
	
	def __init__(self, verbose=False):
		self.closed = False
		self.imdb   = imdb_wrapper.IMDBWrapper()
		self.status = DialogManager.INIT
		self.verbose = verbose
		self.localdb = LocalDBWrapper()
		self.pagesize = 10
		self.list = []
		self.page = 1
		self.userName = ""
		self.outputType = 3
		self.w1 = self.localdb.getW1()
		self.w2 = self.localdb.getW2()
		self.w3 = self.localdb.getW3()
		self.quizCounter = 0
		
	def processUserName(self, name):
		self.userName = name
		return self.localdb.load_preference(name)
		
	def loadOptions(self):
		self.outputType = self.localdb.getOutputType()
		self.w1 = self.localdb.getW1()
		self.w2 = self.localdb.getW2()
		self.w3 = self.localdb.getW3()
	
	def saveUserPreferences(self):
		self.localdb.store_preference(self.userName)
		
	# nluoutput : EntitySet
	def process(self, nluoutput):
		entities  = self.processPronouns(nluoutput)
		#if (self.verbose): print "EntitySet: " + entities.toString()
			
		if self.status == DialogManager.PAGING:
			if nluoutput.classifier == "next"\
				and self.page < int(math.ceil(len(self.list)/self.pagesize)):
				dmoutput = DmOutput("recommendationsPaging", True)
				self.page = self.page + 1
				self.processPaging(self.page, dmoutput)
				return dmoutput
			elif nluoutput.classifier == "back"\
				and self.page > 1:
				dmoutput = DmOutput("recommendationsPaging", True)
				self.page = self.page - 1
				self.processPaging(self.page, dmoutput)
				return dmoutput
			else:
				self.status = DialogManager.INIT
					
		if self.status == DialogManager.ASKINGFORLIKES:
			if nluoutput.classifier == "answer"\
				and nluoutput.has_entity("yesno")\
				and nluoutput.find_entity("yesno") == "no":
				self.status = DialogManager.ASKINGFORREC
				return DmOutput("askingForRecommendation")
			else: self.status = DialogManager.INIT
			
		if self.status == DialogManager.ASKINGFORREC:
			if nluoutput.classifier == "answer"\
				and nluoutput.has_entity("yesno")\
				and nluoutput.find_entity("yesno") == "yes":
					return self.processRecommendMovie(entities)
			else: self.status = DialogManager.INIT
		
		# process input in initial state
		if self.status == DialogManager.INIT:
			
			if nluoutput.classifier == "userPreference":
				return self.processUserPreference(entities)
			elif nluoutput.classifier == "recommend":
				return self.processRecommendMovie(entities)
			elif nluoutput.classifier == "trivia":
				return self.processTrivia(entities)
			elif nluoutput.classifier == "trivia_yesno":
				return self.processTriviaConfirm(entities)
			elif nluoutput.classifier == "list":
				return  self.processList(entities)
			elif nluoutput.classifier == "answer":
				return self.processAnswer(entities)
			elif nluoutput.classifier == "bye":
				#self.closed = True
				#dmoutput = DmOutput("quitting")
				dmoutput = DmOutput("quiz1")
				self.status = DialogManager.QUIZZING
				return dmoutput
			elif nluoutput.classifier == "unknown":
				return self.processUnknown(entities)
		elif self.status == DialogManager.QUIZZING:
			
			if nluoutput.classifier == "bye":
				self.closed = True
				return DmOutput("quitting")
			
			self.quizCounter += 1
			if nluoutput.classifier == "answer"\
				and nluoutput.has_entity("yesno")\
				and nluoutput.find_entity("yesno") == "no":
				if (self.quizCounter == 1):
					self.closed = True
					return DmOutput("quitting")
				elif (self.quizCounter == 2):
					
					# CHANGE SCORE CALCULATION VARIABLES HERE AND SAVE TO LOCAL FILE
					w1_diff = self.w1 - 0.3
					w2_diff = self.w2 - 1.0
					w3_diff = self.w3 - 1.0
					
					if w1_diff == w2_diff and w2_diff == w3_diff:
						self.w3 += random.randrange(1, 4) * 0.1
					else:
						dec = random.randrange(1,4) * 0.1
						if w1_diff >= w2_diff and w1_diff >= w3_diff:	# w1 - max
							self.w1 -= dec 
						elif w2_diff >= w1_diff and w2_diff >= w3_diff:
							self.w2 -= dec
						elif w3_diff >= w1_diff and w3_diff >= w2_diff:
							self.w3 -= dec
						
						if w3_diff <= w1_diff and w3_diff <= w2_diff:  # w3 - min
							self.w3 += dec
						elif w2_diff <= w1_diff and w2_diff <= w3_diff:
							self.w2 += dec
						elif w1_diff <= w2_diff and w1_diff <= w3_diff:	
							self.w1 += dec
					
					# implement weighted sum 
					
					self.localdb.setWValues(self.w1, self.w2, self.w3)
					return DmOutput("changingScoreCalculation")
				else:
					
					# CHANGE OUTPUT TYPE HERE AND SAVE TO LOCAL FILE
					self.outputType += 1
					if (self.outputType == 5): self.outputType = 1
					self.localdb.setOutputType(self.outputType)
					self.closed = True
					return DmOutput("changingOutputType")
			else:
				if (self.quizCounter == 1):
					return DmOutput("quiz2")
				elif (self.quizCounter == 2):
					
					return DmOutput("quiz3")
				else:
					self.closed = True
					return DmOutput("thanksForAnswering")

		return DmOutput("nothing")

	def processPronouns(self, nluoutput):
		return nluoutput
	
	
	def processPaging(self, pagenumber, dmoutput):
		
		dmoutput.setPageNumber(pagenumber)
		dmoutput.setTotalPages(int(math.ceil(len(self.list)/self.pagesize)))
		
		start = (pagenumber-1) * self.pagesize
		end   = pagenumber * self.pagesize
		counter = 1
		for x in range(start,end):
			if x == len(self.list):
				break
			movie = self.list[x]
			item = ListItem()
			item.add_entity("listNumber", (pagenumber-1)*self.pagesize+counter)
			item.add_entity("name", movie.get_title())
			item.add_entity("year", movie.get_year())
			item.add_entity("score", movie.get_score())
			dmoutput.add_listitem(item)
			counter += 1
			
	def processPagingIMDB(self, pagenumber, dmoutput):
		start = (pagenumber-1) * self.pagesize
		end   = pagenumber * self.pagesize
		for x in range(start,end):
			movie = self.list[x]
			item = ListItem()
			item.add_entity("name", movie["title"])
			item.add_entity("year", movie["year"])
			dmoutput.add_listitem(item)
	
	def getMovieTitle(self, entities):
		title = ""
		if not entities.has_entity("movieTitle"):
				if entities.has_entity("person"):	# handle wrong classification
					title = entities.find_entity("person")
				else:
					return title
		else:
			title = entities.find_entity("movieTitle")
		return title
	
	# processes 'I like action movies.'
	def processUserPreference(self, entities):
			
		if entities.has_entity("rating") == True:
			rating = entities.find_entity("rating")
			
			value = ""
			
			if entities.has_entity("movieTitle") == True:
				value  = entities.find_entity("movieTitle")
				self.localdb.add_preference("movie", value, rating)
			
			if entities.has_entity("movieTitle2") == True:
				value  = entities.find_entity("movieTitle")
				self.localdb.add_preference("movie", value, rating)
				
			if entities.has_entity("genre") == True:
				value  = entities.find_entity("genre")
				self.localdb.add_preference("genre", value, rating)
			
			if entities.has_entity("genre2") == True:
				value  = entities.find_entity("genre2")
				self.localdb.add_preference("genre2", value, rating)
					
			if entities.has_entity("person") == True:
				value  = entities.find_entity("person")
				self.localdb.add_preference("person", value, rating)

			if entities.has_entity("person2") == True:
				value  = entities.find_entity("person")
				self.localdb.add_preference("person", value, rating)

			if entities.has_entity("person3") == True:
				value  = entities.find_entity("person")
				self.localdb.add_preference("person", value, rating)

			if entities.has_entity("director") == True:
				value  = entities.find_entity("director")
				self.localdb.add_preference("director", value, rating)

			if value != "":
				self.status = DialogManager.ASKINGFORLIKES
				dmOutput = DmOutput("preferenceProcessed")
				return dmOutput
			
		dmOutput = DmOutput("couldNotUnderstandPreference")
		return dmOutput
		
		
	# processes 'Recommend me a movie.'
	def processRecommendMovie(self, entities):
		#Tell DB to return a movie title based on saved user preferences
		userpref = self.localdb.get_preference()
		self.list = []
		if (self.outputType == 1):
			reclist = self.imdb.get_recommendation(entities,userpref)
			for movie in reclist:
				self.list.append(movie)
			dmOutput = DmOutput("recommendations", False, "")
			self.page = 1
			self.processPaging(self.page,dmOutput)
			self.status = DialogManager.PAGING
		elif (self.outputType == 2):
			reclist = self.imdb.get_recommendation_randomlist(entities,userpref)
			for movie in reclist:
				self.list.append(movie)
			dmOutput = DmOutput("recommendations", False, "")
			self.page = 1
			self.processPaging(self.page,dmOutput)
			self.status = DialogManager.PAGING
		elif (self.outputType == 3):
			movie = self.imdb.get_recommendation_onebest(entities,userpref)
			self.list.append(movie)
			dmOutput = DmOutput("recommendOne", False, movie.get_title()+" ("+str(movie.get_year())+")")
		else :
			movie = self.imdb.get_recommendation_onerandom(entities,userpref)
			self.list.append(movie)
			dmOutput = DmOutput("recommendOne", False, movie.get_title()+" ("+str(movie.get_year())+")")
		
		return dmOutput
	
	
	def processTrivia(self, entities):
		if len(entities.get_entitylist()) == 1 or not entities.has_entity("type") :
			return DmOutput("notunderstood")
		
		#type, movieTitle, person, range
		
		if entities.has_entity("range"):
			queryrange =  entities.find_entity("range")
		
			# top 250 , bottom 100 movies with paging	
			if queryrange in ("top", "bottom"):
				self.status = DialogManager.PAGING
				self.page = 1
				self.pagesize = 10

			if queryrange == "top":
				dmoutput = DmOutput("topratingmovies", True)
				self.list =  self.imdb.get_top250()

			if queryrange == "bottom":
				dmoutput = DmOutput("worstmovies", True)
				self.list =  self.imdb.get_bottom100()
				
			self.page = 1
			self.processPagingIMDB(self.page, dmoutput)

			return dmoutput
		
		querytype = entities.find_entity("type")
		querytype = querytype.lower().strip()
		if querytype == "plot":
			title = self.getMovieTitle(entities)
			if title == "":
				return DmOutput("insufficientparameter")
				
			plot = self.imdb.get_plot(title)
			if plot == "":
				s = DmOutput("notavailable", False, title)
				return s	
			else:
				s = DmOutput("plot", False, title)
				item = ListItem()
				item.add_entity("plot", plot)
				s.add_listitem(item)
				return s
				
		if querytype == "cast" or querytype == "actor":
			if entities.has_entity("movieTitle"):
				castlist = self.imdb.get_castlist(entities.find_entity("movieTitle"))
				if len(castlist) == 0:
					return DmOutput("notavailable", False, entities.find_entity("movieTitle"))
				else:
					s = DmOutput("cast", False, entities.find_entity("movieTitle"))
					for person in castlist:
						item = ListItem()	
						item.add_entity("name", person)
						s.add_listitem(item)
						
					#self.list = castlist
					#self.page = 1
					#self.processPaging(self.page, s)
					#self.status = DialogManager.PAGING
					
					return s
		
		if querytype == "movietitle":
			self.list = self.imdb.get_movielist(entities)
			needpaging = False
			self.page = 1
			self.pagesize = 10
			
			if len(self.list) == 0:
				return DmOutput("notavailable")
			
			if len(self.list) > 10:
				self.status = DialogManager.PAGING
				needpaging = True

			dmoutput = DmOutput("movielist", needpaging)
				
			self.page = 1
			self.processPaging(self.page, dmoutput)
			
			return dmoutput
		
		if querytype == "director":
			title = self.getMovieTitle(entities)
			if title == "":
				return DmOutput("insufficientparameter")
						
			director = self.imdb.get_director(title)

			if director == "":
				return DmOutput("notavailable", title)
			else:
				s = DmOutput("director", False, title)
				item = ListItem()	
				item.add_entity("name", director)
				s.add_listitem(item)						
				return s
		
		return DmOutput("notunderstood")
	
	# processes various other trivia questions
	def processTriviaConfirm(self, entities):
		
		name = ""
		
		if not entities.has_entity("movieTitle"):
			return DmOutput("notunderstood")
		
		movie = entities.find_entity("movieTitle")
		
		if entities.has_entity("director"):
			name = entities.find_entity("director") 
			director = self.imdb.get_director(movie)
			print "DIRECTOR: " + director
			
			if director == "":
				return DmOutput("notavailable", movie)
			else:
				director = "'"+director+"'"
				name2 = self.imdb.encodeName(name)
				print "CMP: " + name2 + "=?" + director
				result = director == name2
					
		elif entities.has_entity("actor"):
			name = entities.find_entity("actor") 
			result = self.imdb.is_person_in_movie(name, movie) 
		elif entities.has_entity("person"):
			name = entities.find_entity("person")
			result = self.imdb.is_person_in_movie(name, movie) 
		
		if name != "":
			if result:
				s = DmOutput("INTHERE", False, movie)
				item = ListItem()
				item.add_entity("name", name)
				s.add_listitem(item)
				return s
			else:
				s = DmOutput("NOTTHERE", False, movie)
				item = ListItem()
				item.add_entity("name", name)
				s.add_listitem(item)
				return s
		
		return DmOutput("notunderstood")
	
	
	
	def processList(self, entities):

		if entities.has_entity("type"):
			type = entities.find_entity("type")
			
			if type != "movieTitle":
				return self.processTrivia(entities)
							
		#Tell DB to return a movie title based on saved user preferences
		reclist = self.imdb.get_movielist(entities)
		
		self.list = []
		for movie in reclist:
			self.list.append(movie)
		
		dmOutput = DmOutput("movielist", False, "")
		self.page = 1
		self.processPaging(self.page,dmOutput)
		self.status = DialogManager.PAGING

		return dmOutput

	# processes answers
	def processAnswer(self, entities):
					
		return DmOutput("nothing")
	
	def translateYesNo(self, entities):
		if (entities.has_entity("yesno")):
				if (entities.find_entity("yesno") == "yes"):
					return 2
				else: return 1
		else : return 0
		
	# processes unknown
	def processUnknown(self, entities):
		return DmOutput("notunderstood")

	def sessionclosed(self):
		return self.closed