'''

Natural Language Generator

Created on Jan 28, 2011

@author: yangwookkang
'''

class NLgenerator:
	
	MOVIELIST = "{name:s} ({year:d})"
	RECOMMENDATION = "{listNumber:d}. {name:s} ({year:d})"
	CASTLIST = "{name:s}"
	
	RECOMMENDATIONS = "Here is a list of recommendations."
	AFTERRECOMMENDATIONS = ("This is page {page:d} of {totalpages:d}.\n"
		"You can change pages by typing next, \n"
		"or give me another command.")
	AFTERPAGINGRECOMMENDATIONS = ("This is page {page:d} of {totalpages:d}.\n"
		"You can change pages by typing back or next, \n"
		"or give me another command.")
	RECOMMENDONE = ("I recommend {name:s}.\n"
		"If you'd like a different recommendation,\n"
		"tell me some more of your likes or dislikes.")
	PREFERENCEPROCESSED = "Alright. Is there anything else you like or dislike?"
	ASKINGFORRECOMMENDATION = "OK. Would you like a recommendation now?"
	NOTUNDERSTOOD = "Wouldn't you like to talk about something else? Tell me about movies, genres, actors, and directors you like, and I'll recommend you a movie."
	TOPRATINGMOVIES = "The followings are top rating movies, say 'next' if you would like to see more."
	WORSTMOVIES = "The followings are worst movies ever, say 'next' if you would like to see more."
	MOVIESEARCH = "Here's the list of movies I found:"
	PLOT = "Here's the plot of {name:s}"
	NOTAVAILABLE = "Sorry, we searched the database, but couldn't find any information"
	DIRECTOR = "The director of {movietitle:s} is {directorname:s}"
	CAST = "Here's the cast list of movie {name:s}"
	QUITCONFIRM = "Are you sure you want to quit?"
	NOTHING = "Tell me some things you like or dislike, and then ask me for a recommendation."
	COULDNOTUNDERSTANDPREFERENCE = ("Please tell me about some movies, genres, actors, or directors you like.\n"
		"Put movie titles in quotes; For example: I like \"Inception\".")
	QUITTING = "Thank you for using YARB. Goodbye!"
	QUIZ1 = "Before you quit, would you like to answer a quick survey?"
	QUIZ2 = "Did you find the movies that were recommended satisfactory?"
	QUIZ3 = "Did you think that the way the movies were displayed (single or list) was satisfactory?"
	CHANGINGSCORECALCULATION = ("OK. We'll change the way we calculate the recommendations next time.\n"
		"Did you think that the way the movies were displayed (single or list) was satisfactory?")
	CHANGINGOUTPUTTYPE = ("OK. We'll change the way we display the recommendations next time.\n"
		"Thanks for answering the questions. Quitting now...")
	THANKSFORANSWERING = "Thanks for answering the questions. Quitting now..."
	INTHERE = "Yes, {name:s} is affiliated with \"{title:s}\""
	NOTTHERE = "No, {name:s} is not affiliated with \"{title:s}\""
	
	
	def __init__(self, verbose=False):
		self.test = 0
		self.verbose = verbose
		pass
		
	def process(self, dmoutput):
		msg = []
		# generate an output based on a template
		if dmoutput.get_classifier() == "movielist":
			msg.append(NLgenerator.MOVIESEARCH)
			line = 1
			for movies in dmoutput.get_items():
				msg.append(str(line) + ". " + NLgenerator.MOVIELIST.format(name=movies.find_entity("name"), year=movies.find_entity("year")))
				line = line + 1
		elif dmoutput.get_classifier() == "recommendations":
			msg.append(NLgenerator.RECOMMENDATIONS)
			for movies in dmoutput.get_items():
				msg.append(NLgenerator.RECOMMENDATION.format(listNumber=movies.find_entity("listNumber"), name=movies.find_entity("name"), year=movies.find_entity("year")))
			msg.append(NLgenerator.AFTERRECOMMENDATIONS.format(page=dmoutput.getPageNumber(), totalpages=dmoutput.getTotalPages()))
		elif dmoutput.get_classifier() == "recommendationsPaging":
			for movies in dmoutput.get_items():
				msg.append(NLgenerator.RECOMMENDATION.format(listNumber=movies.find_entity("listNumber"), name=movies.find_entity("name"), year=movies.find_entity("year")))
			msg.append(NLgenerator.AFTERPAGINGRECOMMENDATIONS.format(page=dmoutput.getPageNumber(), totalpages=dmoutput.getTotalPages()))
		elif dmoutput.get_classifier() == "recommendOne":
			msg.append(NLgenerator.RECOMMENDONE.format(name=dmoutput.get_movietitle()))
		elif dmoutput.get_classifier() == "preferenceProcessed":
			msg.append(NLgenerator.PREFERENCEPROCESSED)
		elif dmoutput.get_classifier() == "askingForRecommendation":
			msg.append(NLgenerator.ASKINGFORRECOMMENDATION)
		elif dmoutput.get_classifier() == "notunderstood":
			msg.append(NLgenerator.NOTUNDERSTOOD)
		elif dmoutput.get_classifier() == "topratingmovies":
			msg.append(NLgenerator.TOPRATINGMOVIES)
			line = 1
			for movies in dmoutput.get_items():
				msg.append(str(line) + ". " + NLgenerator.MOVIELIST.format(name=movies.find_entity("name"), year=movies.find_entity("year")))
				line = line + 1
		elif dmoutput.get_classifier() == "worstmovies":
			msg.append(NLgenerator.WORSTMOVIES)
			line = 1
			for movies in dmoutput.get_items():
				msg.append(str(line) + ". " + NLgenerator.MOVIELIST.format(name=movies.find_entity("name"), year=movies.find_entity("year")))
				line = line + 1
		elif dmoutput.get_classifier() == "plot":
			msg.append(NLgenerator.PLOT.format(name=dmoutput.get_movietitle()))
			msg.append(dmoutput.get_items()[0].find_entity("plot"))
		elif dmoutput.get_classifier() == "notavailable":
			msg.append(NLgenerator.NOTAVAILABLE)
		elif dmoutput.get_classifier() == "director":
			msg.append(NLgenerator.DIRECTOR.format(movietitle=dmoutput.get_movietitle(), directorname = dmoutput.get_items()[0].find_entity("name") ))
		elif dmoutput.get_classifier() == "cast":
			msg.append(NLgenerator.CAST.format(name=dmoutput.get_movietitle()))
			line = 1
			for movies in dmoutput.get_items():
				msg.append(str(line) + ". " + NLgenerator.CASTLIST.format(name=movies.find_entity("name")))
				line = line + 1
		elif dmoutput.get_classifier() == "quitConfirm":
			msg.append(NLgenerator.QUITCONFIRM)
		elif dmoutput.get_classifier() == "nothing":
			msg.append(NLgenerator.NOTHING)
		elif dmoutput.get_classifier() == "couldNotUnderstandPreference":
			msg.append(NLgenerator.COULDNOTUNDERSTANDPREFERENCE)
		elif dmoutput.get_classifier() == "quitting":
			msg.append(NLgenerator.QUITTING)
		elif dmoutput.get_classifier() == "quiz1":
			msg.append(NLgenerator.QUIZ1)
		elif dmoutput.get_classifier() == "quiz2":
			msg.append(NLgenerator.QUIZ2)
		elif dmoutput.get_classifier() == "quiz3":
			msg.append(NLgenerator.QUIZ3)
		elif dmoutput.get_classifier() == "changingOutputType":
			msg.append(NLgenerator.CHANGINGOUTPUTTYPE)
		elif dmoutput.get_classifier() == "changingScoreCalculation":
			msg.append(NLgenerator.CHANGINGSCORECALCULATION)
		elif dmoutput.get_classifier() == "thanksForAnswering":
			msg.append(NLgenerator.THANKSFORANSWERING)
		elif dmoutput.get_classifier().lower() == "inthere":
			msg.append(NLgenerator.INTHERE.format(name= dmoutput.get_items()[0].find_entity("name"), title=dmoutput.get_movietitle() ))	
		elif dmoutput.get_classifier().lower() == "notthere":
			msg.append(NLgenerator.NOTTHERE.format(name= dmoutput.get_items()[0].find_entity("name"), title=dmoutput.get_movietitle() ))
		
		else:
			if (self.verbose == True):
				msg.append("NLG classifier: "+dmoutput.get_classifier())
				
		return "\n".join(msg)