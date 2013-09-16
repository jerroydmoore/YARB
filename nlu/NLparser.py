'''

Natural Language Parser

public functions:
	* process(utterance) - Returns an EntitySet
	* verbose(Boolean)   - Turn Diagnostic messages off/on
	
private functions:
	* _classify_word
	* _isTreeBranch
	* _isLeaf
	* _getLeafTos
	* _getLeafTxt
	* _getTreeTxt
	* _parse_question
	* _parse_command
	* _find_verbs
	* _parse_as_who
	* _parse_as_what
	* _parse_as_when
	* _parse_as_TF
	* _negator
	* _parse_as_answer
	* _parse_as_userPref
	* _determine_rating
	* _synset_similarity
'''

import nltk
from entity import EntitySet
from nltk.corpus import wordnet as wn
import chunker
import re

class NLparser:

	def __init__(self, verbose=False):
		self.vb = verbose
		
		if self.vb:
			print "NLU: Instantiating chunker"
		else:
			#instead of blank screen, display humanistic behavior message updates!
			print "*yawn* Hold on a second, I just woke up..."
		self.chk = chunker.Chunker(False)
		
		if self.vb:
			print "NLU: Generating adjective synsets"
		else:
			print "*rubs sleepy eyes* One sec! Let me put on a pot of coffee..."
			
		
		self.rating5_list = ['great', 'favorite', 'terrific']
		self.rating4_list = ['like','good','intellectual','funny', 'fun', 'beautiful']
		self.rating2_list = ['dislike','bad','stupid','hack','suck']
		self.rating1_list = ['stupid', 'terrible', 'aweful', 'hate', 'worst']
		
		self.adjectiveSS_list = []
		for x in self.rating5_list:
			self.adjectiveSS_list.append((x, wn.synsets(x)))
		for x in self.rating4_list:
			self.adjectiveSS_list.append((x, wn.synsets(x)))
		for x in self.rating2_list:
			self.adjectiveSS_list.append((x, wn.synsets(x)))
		for x in self.rating1_list:
			self.adjectiveSS_list.append((x, wn.synsets(x)))
		
		self.genre_list = ['thriller', 'short', 'adventure', 'drama', 'music', 'sci-fi', 'action',
		'fantasy', 'horror', 'biography', 'comedy', 'family', 'musical', 'documentary', 'animation',
		'talk-show', 'crime', 'mystery', 'romance', 'romantic', 'history', 'war', 'game-show', 'western', 'sport',
		'reality-tv', 'news', 'film-noir', 'lifestyle', 'adult' ]
		
		"""
		self.adjectiveSS_list = [( "like", wn.synsets('like') ) ]
		self.adjectiveSS_list.append(("dislike", wn.synsets('dislike') ))
		self.adjectiveSS_list.append(("good", wn.synsets('good') ))
		self.adjectiveSS_list.append(("bad", wn.synsets('bad') ))
		self.adjectiveSS_list.append(("stupid", wn.synsets('stupid') ))
		self.adjectiveSS_list.append(("hack", wn.synsets('hack') ))
		self.adjectiveSS_list.append(("suck", wn.synsets('sucked') ))
		self.adjectiveSS_list.append(("see", wn.synsets('see') ))
		self.adjectiveSS_list.append(("think", wn.synsets('think') ))
		self.adjectiveSS_list.append(("funny", wn.synsets('funny') ))
		self.adjectiveSS_list.append(("beautiful", wn.synsets('beautiful') ))
		self.adjectiveSS_list.append(("intellectual", wn.synsets('intellectual') ))
		self.adjectiveSS_list.append(("favorite", wn.synsets('favorite') ))
		"""
		
		if self.vb:
			print "NLU: Generating classifier synsets"
		else:
			print "Almost ready!"

		self.verbToClassifierMapping = {
			'find': 'recommend',
			'see':  'list',
			'show': 'list',
			'tell': 'list',
			'watch': 'recommend',
			'list': 'list',
			'recommend': 'recommend',
			'suggest': 'recommend'
		}
		## verbToSynsets():
		## initiate the synsets for verbs
		self.classifierSS_list = []
		## itor thru, finding the synsets for the verbs and mapping them to the classifiers
		for sVerb,sClassifier in self.verbToClassifierMapping.items():
			theseSS = wn.synsets(sVerb)
			## Find the classifier (if it's been set already)
			for itor,lPairs in enumerate(self.classifierSS_list):
				sNewClassifier = lPairs[0]
				if sClassifier == sNewClassifier:
					## Classifier set, add the synsets to the existing list:
					self.classifierSS_list[itor][1].extend(theseSS)
					break
			else:
				## The classifier did not exist, create it:
				self.classifierSS_list.append((sClassifier, theseSS))		
		
		#print "classifier SS LIST:"
		#for x,y in self.classifierSS_list:
		#	print x,y
		
		self.pronouns = {
			'it': None,
			'person': None
		}

		
	## Classify word into one of the categories in SS_list
	def _classify_word(self, leafnode, local_SSList):
		
		if not self._isLeaf(leafnode):
			return (None, 0)
		
		cword = self._getLeafTxt(leafnode)
		tos = self._getLeafTos(leafnode)
		
		if tos == 'DT' or tos == 'QM' or tos == '.' or tos == 'PRP' or cword == 'is' or cword == 'are':
		#if cword == "." or cword == "is":
			#clean up verbose by simply returning
			return (None, 0)
			
		#if self.vb:
		#	print "Called _classify_word(%s):-" % (cword, )
		
		word_s = wn.synsets(cword)
		score = 0
		match = None
		returnVar = False
		for thisAdj,thisSynset in local_SSList:
			tmp = self._synset_similarity(thisSynset, word_s)
			#if self.vb:
			#	tmp2 = self._OLDsynset_similarity(thisSynset, word_s) 
			#	if tmp >= 0.00001:
			#		print "synsets: %s, %s -> %.05f / %.05f" % (thisAdj, cword, tmp, tmp2)
			
			#if self.vb:
			#	print "Called _synset_similarity(synsets('%s'), synsets('%s')):- %s" % (thisAdj, cword, tmp)
			
			if self.vb:
				print "%s -> %s. %.05f" % (cword, thisAdj, tmp)
			
			if tmp > score:
				score = tmp
				match = thisAdj
			#if score == 1:
			#	break
				#return (match, score)

		if self.vb:
			print "Returning _classify_word(%s):- (%s, %.05f)" % (cword, match, score)
		return (match, score)
	
	## isTreeBranch determines returns true if the parse tree node in argument is of type Tree
	## returns true/fase
	def _isTreeBranch(self, parsetree):
		return "Tree" in str(type(parsetree))
		
	## isLeaf determines returns true if the parse tree node in argument is of type Tuple, indicating a leaf node
	## returns true/fase
	def _isLeaf(self, parsetree):
		return "tuple" in str(type(parsetree))
	
	## Gets the TOS ("Tag of Speech") The chunker classified the leaf as
	## Returns a string
	## If leaf is not a leaf, returns ""
	def _getLeafTos(self, leaf):
		ret = ""
		if self._isLeaf(leaf):
			ret = leaf[1]
		return ret
		
	## Gets the text of the leaf
	## Returns a string
	## If leaf is not a leaf, returns ""
	def _getLeafTxt(self, leaf):
		ret = ""
		if self._isLeaf(leaf):
			ret = leaf[0]
		return ret
	
	## Takes a flat chunk subtree (one with only tuples -- no subtrees) 
	##	and returns its untagged string representation.
	def _getTreeTxt(self, subtree):
		first_quotes = False
		string_rep = ""
		for x in subtree:
			if (x[1] != ":") : 
				string_rep += x[0]
				string_rep += " "
			elif first_quotes == False:
				first_quotes = True
			else:
				break
				#return string_rep.rstrip()
		
		if self.vb:
			print "Called _getTreeTxt(%s):- %s" % (subtree.node, string_rep.rstrip())
		
		return string_rep.rstrip()
	
	##	Question parser: Takes a chunk tree and returns a tuple of strings to pass
	## to a dialog manager.
	##
	## function converted. "why" is not implemented
	def _parse_question(self, chktree):
		if self.vb:
			print "Called _parse_question(chktree):- EntitySet"
			#chktree.draw()
		
		#if chktree[0][0][1] == 'MD':
		#	entSet = self._parse_as_what(chktree)
		questionNode = chktree[0]
		qtype = None
		for x in questionNode:
			if self._isLeaf(x):
				tos = self._getLeafTos(x)
				if tos == 'MD':
					qtype = 'what'
				elif tos.startswith('W'):
					qtype = self._getLeafTxt(x).lower()
			if qtype != None:
				break
			
		#if self._isTreeBranch(chktree[0][0]):
		#	qtype = self._getLeafTxt(chktree[0][0][0]).lower
		#	tos = self._getLeafTos(chktree[0][0][0])
		#elif self._isLeaf(chktree[0][0]):
		#	qtype = self._getLeafTxt(chktree[0][0]).lower()
		#	tos = self._getLeafTos(chktree[0][0])
		
		#if tos == 'MD':
		#	entSet = self._parse_as_what(chktree)
		if qtype == "who":
			entSet = self._parse_as_who(chktree) 	
		elif qtype == "what" or qtype == 'which':
			entSet = self._parse_as_what(chktree) 	
		elif qtype == "when":
			entSet = self._parse_as_when(chktree) 	
		#elif qtype == "why":
		#	entSet = self._parse_as_why(chktree) 
		else:
			entSet = self._parse_as_TF(chktree) 

		return entSet
	
	## Command Parser. Takes "(I would like to) see...."
	def _parse_command(self, chunked):
		if self.vb:
			print "Called _parse_command(chktree):- EntitySet"
		entSet = False
		
		'''
		cmd_node = chunked[0]
		verbs = self._find_verbs(cmd_node)
		
		theVerb = None
		if len(verbs) == 1:
			theVerb = verbs[0].lower()
			if theVerb == 'know':
				#I would like to know directed "Twilight"?
				#know the cast of "Ocean's 11"?
				#Do you know which movies Keanu Reeves is in?
				return self._rechunk(chunked)
			else:
				theVerb = verbs[0]
				#theClassifier = self.verbToClassifierMapping.get(verbs[0].lower(), "unknown")
		elif len(verbs) == 0:
			# Just in Case Error-Catch
			if vb.self:
				print "NLU Error: Parsing COMMAND node resulted in no VB node. Impossible; grammar does not allow this"
			pass
		else:
			#TODO: Will this happen? (will there ever be more than one verb in command node?
			# if so, program!
			#theClassifier = self.verbToClassifierMapping.get(verbs[0].lower(), "unknown")
			theVerb = verbs[0]
		'''
		theClassifier = None
		theVerb = None #debugging var
		score = 0.0
		negator = False
		for x in chunked[0]:
			#ensure this isn't an adverb
			if self._isLeaf(x) and self._getLeafTos(x)[0] == 'V':
				theClassifier,score = self._classify_word(x, self.classifierSS_list)
				theVerb = self._getLeafTxt(x)
				negator = self._negator(theVerb, negator)
				break
			#elif self._isTreeBranch(x):
				#for y in x:
					#if self._isLeaf(y):
						#negator = self._negator(y)
				
		#theClassifier,score = self._classify_word(theVerb, self.classifierSS_list)
		if self.vb:
			print "parse_cmd: %s -> %s with score %.05f" % (theVerb, theClassifier, score)
		if theClassifier == None or score < .25:
			theClassifier = "unknown"

		type = False
		for itor,x in enumerate(chunked):
			if itor < 1:
				continue
			if self._isTreeBranch(x): ## this shouldn't happen, but just in case
				continue
			
			tagOfSpeech = self._getLeafTos(x)
			theWord = self._getLeafTxt(x)
			negator = self._negator(theWord, negator)
			
			## stage look-forward or look-backward:
			keyword = ""
			if tagOfSpeech == 'KW_DIRECTOR':
				type = "director"
			elif tagOfSpeech == 'KW_STAR':
				type = 'actor'
			elif tagOfSpeech == 'KW_GENRE':
				type = 'genre'
			elif tagOfSpeech == 'KW_PLOT':
				type = 'plot'
				theClassifier = 'trivia'
			elif tagOfSpeech == 'KW_MOVIE' or tagOfSpeech == 'GNRE':
				## include GNRE to catch sentences, such as "I want to watch a Comedy"
				type = 'movieTitle'
				itorBackTrack = itor
				while itorBackTrack > 0:
					y = chunked[itorBackTrack]
					if self._isTreeBranch(y):
						break
					yTos = self._getLeafTos(y)
					if yTos.startswith('JJ') or yTos.startswith('NN'):
						adj, score = self._classify_word(y, wn.synsets('recent'))
						if score > .25:
							entSet.add_entity('timespan', 'recent')
						else:
							adj, score = self._classify_(y, wn.synset('old'))
							
							#'recent'
							#'old'
							#'new'
							#'first'
							#'last'
							#'popular'
							#'similar'
							#'more'
							
					else:
						break
			if type:
				break

		entSet = EntitySet(theClassifier)
		entSet.add_entity("type", type)
		
		entSet = self._parse_entity_pairs(chunked, entSet)
		entSet.remove_entity('rating')

		return [ entSet ]
	
	## _find_verbs( subtree, # a chunked utterance
	##              inVPnode # Because this is a recursive function, and the parse tree can look like anything
	##                       # ignore other nodes unless in a VP branch
	## returns a list of verbs found in VP. From which a classifier may be derived from
	## Algorithm is DFS, examines only the leafs for verbs, and only only the leafs of VP branches
	def _find_verbs(self, subtree, inVPnode = False):
		if self.vb:
			print "Called _find_verbs(%s, %s):- list" % (subtree.node, inVPnode, )

		listOfVerbs = []
		for x in subtree:
			if self._isTreeBranch(x):
			#if ( "Tree" in str(type(x)) ):
				## Skip REQ nodes, they're meaningless (in the form of "I would like...")
				#print "found tree %s" % (x, )
				if x.node == 'REQ':
					continue
				#This may not execute
				elif x.node == "VP":
					listOfVerbs.extend(self._find_verbs(x, True))
			else:
				#print "found %s/%s" % (x[0], x[1])
				if x[1] == "VB" or (inVPnode and x[1][0] == 'V'):
					## Only look at leafs that are of type V.*
					#print "adding %s" % (x[0], )
					listOfVerbs.append(x[0])
		
		if self.vb:
			print "Returned _find_verbs(%s, %s):- %s" % (subtree.node, inVPnode, listOfVerbs)
		return listOfVerbs
		
	## 'Who' question parser
	##
	##
	## grabEntities too complicated
	##  * Need type
	##  * don't need kw_genre, kw_plot, kw_movie, gnre, or rating
	def _parse_as_who(self, chktree):
		if self.vb:
			print "Called _parse_as_who(chktree):- EntitySet"

		entSet = EntitySet("trivia", self.vb)
		negation = False
		looking_for = 'person'
		for x in chktree:
			if self._isLeaf(x):
				negation = self._negator(self._getLeafTxt(x), negation)
				
				keyword = None
				if self._getLeafTos(x) == "KW_DIRECTOR":
					keyword = 'director'
				elif self._getLeafTos(x) == "KW_STAR":
					keyword = 'actor'

				if keyword:
					if not entSet.has_entity('type'):
						entSet.add_entity('type', keyword)
					else:
						looking_for = keyword
			else:
				if x.node == "TITLE":
					entSet.add_entity2("movieTitle", self._getTreeTxt(x), negation)
					negation = False
				elif x.node == "PERSON":
					personName = self._getTreeTxt(x)
					if not entSet.has_entity('type'):
						entSet.add_entity('type', 'person')
						entSet.add_entity('character', personName)
					else:
						entSet.add_entity2(looking_for, personName, negation)
						negation = False
		
		if entSet.count_entities() == 0:
			#empty entitySet -> unable to parse utterance -> let DM know
			entSet.change_classifier("unknown")
		elif not entSet.has_entity('type'):
			entSet.add_entity('type', 'person')
		
		return [ entSet ]
		
	## 'What' question parser
	##
	def _parse_as_what(self, chktree):
		if self.vb:
			print "Called _parse_as_what(%s):- EntitySet" % (chktree.node)
		
		entSet = EntitySet("trivia", self.vb)
		looking_for = 'other'
		negation = False
		
		## Shouldn't need this with changes to KW_PLOT below:
		'''
		flat = chktree.leaves()
		if flat[ len(flat) - 1 ][1] == ":":
			last = flat[ len(flat) - 2 ]
		else:
			last = flat[ len(flat) - 1 ]
		if last[1] == "KW_PLOT":
			entSet.add_entity("type", "plot")
		'''
		for itor,x in enumerate(chktree):
			if self._isLeaf(x):
				nodetype = self._getLeafTos(x)
				nodetxt = self._getLeafTxt(x)
				if not entSet.has_entity('type'):
					if nodetype == "KW_YEAR":
						return self._parse_as_when(chktree)
					elif nodetype == "KW_DIRECTOR" or nodetype == "KW_STAR":
						next = chktree[itor+1]
						if self._isTreeBranch(next) and next.node == 'PERSON':
							looking_for = 'actor'
							if nodetype == 'KW_DIRECTOR':
								looking_for = 'director'
						else:	
							return self._parse_as_who(chktree)
					elif nodetype == "KW_GENRE":
						entSet.add_entity("type", "genre")
					elif nodetype == "KW_MOVIE":
						entSet.add_entity("type", "movieTitle")
					elif nodetype == "KW_PLOT":
						entSet.add_entity("type", "plot")
					elif nodetype == "GNRE":
						entSet.add_entity("type", "movieTitle")
						entSet.add_entity("genre", nodetxt)
				else:
					negation = self._negator(nodetxt, negation)
					if nodetype == 'POS':
						## We mis-categorized the type.
						## Ex: "What was director Michael Bay's latest movie?"
						## Director is not what the user is looking for. director describes Michael Bay, which describes movie.
						#if entSet.has_entity('type'):
						#	looking_for = entSet.find_entity('type')
						#	if looking_for = 'director' or looking_for == 'actor'
						pass
					if nodetype == "KW_DIRECTOR":
						looking_for = "director"
					elif nodetype == "KW_STAR":
						looking_for = "actor"
					elif nodetype == "KW_PLOT":
						#looking_for = "plot"
						## TODO: TEST THIS
						entSet.add_entity('type', 'plot')
					elif nodetype == "GNRE":
						entSet.add_entity2('genre', nodetxt, negation)
						negation = False
						
			else:
				if x.node == "TITLE":
					entSet.add_entity2('movieTitle', self._getTreeTxt(x), negation)
				elif x.node == "PERSON":
					subject = looking_for
					if looking_for == 'other':
						subject = 'person'
					
					entSet.add_entity2(subject, self._getTreeTxt(x), negation)
					negation = False
		return [ entSet ]
					

	## 'When' question parser
	## function converted; remove parameter_list when done
	##
	## function done; delete parameter_list
	def _parse_as_when(self, chktree):
		if self.vb:
			print "Called _parse_as_when(chktree):- EntitySet"
		
		entSet = EntitySet("trivia", self.vb)
		parameter_list = ["year"]
		entSet.add_entity("type", "year")
		found_subject = False
		for x in chktree:
			if self._isTreeBranch(x):
			#if "Tree" in str(type(x)) :
				if x.node == "TITLE":
					found_subject = True
					parameter_list.append('title')
					parameter_list.append(self._getTreeTxt(x)) 
					entSet.add_entity("movieTitle", self._getTreeTxt(x))
				elif x.node == "PERSON":
					found_subject = True
					parameter_list.append('person')
					parameter_list.append(self._getTreeTxt(x)) 
					entSet.add_entity("person", self._getTreeTxt(x))

		if found_subject == False:
			parameter_list.append('other')
			parameter_list.append('that')
			print "_parse_as_when: append 'other' and 'that' to parameter_list"

		#return parameter_list
		return [ entSet ]

	## True/False question parser
	## Plot / director / actor
	##
	## function converted; delete parameter_list
	def _parse_as_TF(self, chktree):
		if self.vb:
			print "Called _parse_as_TF(chktree):- EntitySet"
		
		entSet = EntitySet("trivia_yesno", self.vb)
		entSet = self._parse_entity_pairs(chktree, entSet)
		return [ entSet ]
		
		## Ignore the rest:
		looking_for = "person"
		negation = False
		parameter_list = []
		for x in chktree:
			if self._isLeaf(x):
			#if "tuple" in str(type(x)):
				negation = self._negator(x[0], negation)
				if x[1] == "CD":
					parameter_list.append('year')
					parameter_list.append(x[0])
					entSet.add_entity("year", x[0])
				elif ( x[1] == "KW_DIRECTOR" ):
					looking_for = 'director'
				elif ( x[1] == "KW_STAR" ):
					looking_for = 'actor'
				
				elif x[1] == "KW_PLOT":
					looking_for = "plot"
					
				elif x[1] == "GNRE":
					subject = "genre"
					if negation:
						subject = "!genre"
						parameter_list.append('!genre')
					else:
						parameter_list.append('genre')
					parameter_list.append(x[0].title())
					entSet.add_entity(subject, x[0].title())
			else:
				if x.node == "TITLE":
					parameter_list.append('title')
					parameter_list.append(self._getTreeTxt(x))
					entSet.add_entity("movieTitle", self._getTreeTxt(x))
				elif x.node == "PERSON":
					if looking_for == "actor":
						if negation:
							parameter_list.append('!actor')
						else:
							parameter_list.append('actor')
					elif looking_for == "director":
						if negation:
							parameter_list.append('!director')
						else:
							parameter_list.append('director')
					else:
						if negation:
							parameter_list.append('!person')
						else:
							parameter_list.append('person')

					parameter_list.append(self._getTreeTxt(x))
					entSet.add_entity(looking_for, self._getTreeTxt(x))
		#return parameter_list
		return [ entSet ]
	
	#def _find_adj(self, chktree, itor):
		

	## Takes a word and current negation state.
	def _negator(self, word, neg):
		## could return 'not neg' (flipping the bit)
		#if self.vb:
		#	print "Called negator(%s, %s)" % (word, neg)
		negate = False
		if word == "n't":
			negate = True
		elif word == 'not':
			negate = True
		elif word == 'without':
			negate = True
		elif word == 'but':
			negate = False
		elif word == 'however':
			negate = False
		elif word == 'although':
			negate = False
		elif word == 'besides':
			negate = True
		
		#if neg ^ negate and self.vb:
		#	print "negator flipped! %s -> %s" % (neg, negate)
		return neg ^ negate ## XOR

	## Find the next PERSON or TITLE given a subtree
	## function appears not to be in use
	#def _get_next_subj(self, chktree, index):
	#	i = index + 1
	#	print "Checking", chktree[i]
	#	if ( "Tree" in str(type(chktree[i])) ):
	#		print "x is a tree"
	#		if ( chktree[i].node == "TITLE" ) | ( chktree[i].node == "PERSON" ):
	#			print "Found title or person", chktree[i].node, " :: ", chktree[i]
	#			return self._getTreeTxt(chktree[i])
	#	i += 1
	
	## TODO: Decide if we need to implement this
	def _rechunk(self, oldparsetree):
		if self.vb:
			print "_rechunk not implimented"
		return [ EntitySet("unknown") ]
	
	##	Public function takes user input as a string and returns a list of
	##	tuples of strings where each tuple starts with a dialog classifier
	##	type followed by a number of arguments.
	##
	
	def _prechunking(self, input_string):
		## if the first word is not capitalized, it causes errors
		## if spaces at the beginning -> errors
		
		input_string = input_string.strip()
		if len(input_string) == 0:
			return input_string
		
		## BEGIN: get rid of useless symantics
		## Such as:
		## "Can you..."
		## "Can I..."
		## "I'd like to..."
		## "I'd like to know"
		## "I would like you to..."
		## "I want to..."
		
		prefixs = [
			#"can you",
			#"can i",
			"i'd like to know",
			#"i'd like to",
			"i would like to know",
			#"i would like to",
			#"i want to"
		]
		for x in prefixs:
			#break
			if input_string.lower().startswith(x):
				y = len(x)
				input_string = input_string[y:]
				input_string = input_string.strip()
				break
		'''
		howmany_to_pop = 0
		if len(x) > 5 and 
		elif x[0].lower() == 'can' and (x[1].lower() == 'you' or x[1].lower() ==:
			howmany_to_pop = 2
		elif:
		
		while howmany_to_pop != 0:
			x.pop(0)
			howmany_to_pop -= 1
		'''
		## END: get rid of useless symantics
		
		x = input_string.split()
		x[0] = x[0].capitalize()
		input_string = ' '.join(x)
		return input_string
	
	## NLU.process() is the entry point into the program
	## process() searches for simple keywords
	## or detects an answer utterance
	def process(self, input_string):
	
		#Firstly, trim useless semantics that will muck up the parse tree.
		input_string = self._prechunking(input_string)
		
		#print "INPUT: %s" % (input_string, )
		returnVar = False
		chunked = self.chk.chunk(input_string)
		
		## look for keywords:
		simple_input = input_string.lower()
		if 'start over' in simple_input:
			returnVar = [ EntitySet('restart', self.vb) ]
		elif 'quit' in simple_input:
			returnVar = [ EntitySet('bye', self.vb) ]
		elif 'else' in simple_input or simple_input == 'next':
			returnVar = [ EntitySet('next', self.vb) ]
		elif simple_input == 'back':
			returnVar = [ EntitySet('back', self.vb) ]
		elif simple_input.startswith('it is ') or simple_input.startswith('they are'):
			returnVar = self._parse_answer(chunked)
		else:
			if self.vb:
				print "==BEGIN NLU PROCESSING=="
			
			## MAIN EXECUTION INTO THE PARSING FUNCTIONS: _process()
			## if no simple keywords were found,
			## begin more complex tree traversal
			## to find the correct parsing function
			returnVar = self._process(chunked, 0)
		
		## Execution will only get here if all the parse tree nodes were examined,
		## and no classifier could be determined, including "unknown"
		## If this is the case, we will return an "answer" classifier.
		if returnVar == False:
			## Execution will only get here if the parse tree is a single node of PERSON or TITLE
			
			if self.vb:
				print "Possible Response detected"
				print "tree: %s" % (chunked, )
			
			x = chunked[0]
			returnVar = [ EntitySet("answer", self.vb) ]
			entityName = "unknown"
			if self._isLeaf(x):
				if self.vb:
					print "process: response, unexpected tuple found"
			elif x.node == "PERSON":
				entityName = "person"
			elif x.node == "TITLE":
				entityName = "movieTitle"
			
			returnVar[0].add_entity(entityName, self._getTreeTxt(x))
		
		if 'popular' in simple_input or 'top rating' in simple_input:
			returnVar[0].add_entity('range', 'top')
		elif 'worst' in simple_input:
			returnVar[0].add_entity('range', 'bottom')
		
		#returnVar = self._expandMultiEntitySets(returnVar)
		if True:
			#print "\nClassifier: "
			#print returnVar.get_classifier()
			#print "\nEntities: "
			#returnVar.print_entities()
			for x in returnVar:
				print x.toString()
			#if chunked:
			#	chunked.draw()
				
				
		return returnVar
	
	def _process(self, chunked, startingNode):
		returnVar = False
		#for x in chunked:
		for i,x in enumerate(chunked):
			if i < startingNode:
				if vb.self:
					print "skipping node %d" % (i, )
				continue
			if self._isTreeBranch(x):
				if x.node == "B-QUESTION":
					returnVar = self._parse_question(chunked)
					break
				elif x.node == "COMMAND":
					returnVar = self._parse_command(chunked)
					break
				elif x.node == 'EXISTENTIAL':
					#returnVar = self._parse_existential(chunked)
					returnVar = self._parse_command(chunked)
					returnVar[0].change_classifier('recommend')
					break
				elif x.node == 'REQ':
					returnVar = self._parse_userPref(chunked)
					break
			else:
				nodetype = self._getLeafTos(x)
				if nodetype == 'YES':
					returnVar = [ EntitySet("answer", self.vb) ]
					returnVar[0].add_entity("yesno", "yes")
					break
				elif nodetype == 'NO':
					returnVar = [ EntitySet("answer", self.vb) ]
					returnVar[0].add_entity("yesno", "no")
					break
				elif nodetype == 'HI':
					returnVar = [ EntitySet("hi", self.vb) ]
					break
				elif nodetype == 'BYE':
					returnVar = [ EntitySet("bye", self.vb) ]
					break
				elif nodetype == 'restart':
					returnVar = [ EntitySet("restart", self.vb) ]
					break
				else:
					returnVar = self._parse_userPref(chunked)
					break

		return returnVar
	
	## Allow users to turn off/on verbose mode
	## used in batch testing
	def verbose(self, newValue):
		self.vb = newValue
	
	## last minute architecture change:
	## support multi entSets in a single utterance
	## benefit: supports sentences like: "I like George Cloone and George Lucas"
	def _expandMultiEntitySets(self, entSet):
		if self.vb:
			print "before expanding entSet: %s" % (entSet.toString())
			print ""
		
		returnVar = [ entSet.copy() ]
		for k,v in entSet.get_entityitems():
			x = re.search(r'^(\!)?([^\d]+)(\d+)?', k)
			if not returnVar[0].has_entity('rating'):
				pass
			if x.group(1) and returnVar[0].has_entity('rating'):
				## found '!' and we have something we can inverse 'rating':
				returnVar[0].remove_entity(k)
				#newEntSet = returnVar[0].copy()
				newEntSet = EntitySet(returnVar[0].get_classifier())
				newEntSet.add_entity(x.group(2), v)
				
				## update rating
				theRating = returnVar[0].find_entity('rating')
				if theRating == 5:
					theRating = 1
				elif theRating == 4:
					theRating = 2
				elif theRating == 2:
					theRating = 4
				elif theRating == 1:
					theRating = 5
				newEntSet.add_entity('rating', theRating)
				
				returnVar.append(newEntSet)
			elif x.group(3):
				## numeric value found!
				returnVar[0].remove_entity(k)
				#newEntSet = returnVar[0].copy()
				newEntSet = EntitySet(returnVar[0].get_classifier())
				newEntSet.add_entity(x.group(2), v)
				newEntSet.add_entity('rating', returnVar[0].find_entity('rating'))
				returnVar.append(newEntSet)
		return returnVar
	
	## usually, if the sentence is in the form of 'it is...'
	## this implies it's answering a question of the agent
	def _parse_answer(self, parsetree):
		if self.vb:
			print "Called _parse_answer(parsetree):- EntitySet"
		entSet = EntitySet('answer')
		entSet = self._parse_entity_pairs(parsetree, entSet)
		return [ entSet ]
		
	## Parse sentences starting with a personal pronoun (hopefully the sentence
	## is something like "I like action movies" or "I thought that movie was bad" ).
	def _parse_userPref(self, chktree):
		if self.vb:
			print "Called _parse_userPref(chktree):- EntitySet"
		
		## what will be returned:
		entSet = EntitySet("userPreference", self.vb)
		entSet = self._parse_entity_pairs(chktree, entSet)
		
		if entSet.count_entities() == 0:
			## If there aren't any entity pairs
			## Then perhaps this isn't a userPref utterance.
			## Return Unknown for the DM.
			entSet = EntitySet("unknown")

		return self._expandMultiEntitySets(entSet)
	
	def _parse_entity_pairs(self, chktree, entSet):
		if self.vb:
			print "Called _parse_entity_pairs(chktree, EntitySet):- EntitySet"
		
		## if we do not know what the entity is, clues may be given later in the sentence:
		## this is a list of a leafs
		unclassifiedEntities = []
		## parser works from left to right (ex "... director Clint Eastwood"
		## some english phrases need to work right to left (ex "Clint Eastwood as the director")
		## if classifyUnknowns is True, essentially work backwards.
		## This is implemented by taking from the unclassifiedEntities list
		classifyUnknowns = False
		## Rating element 0 = best guess or rating
		##                1 = probability (or score) that this is correct
		rating = [0, 0.0]

		looking_for = "other"
		negation = False
		#for x in chktree:
		for itor,x in enumerate(chktree):
			if self._isTreeBranch(x):
				if x.node == 'COMMAND': ## check for negation:
					for y in x:
						if self._isTreeBranch(y):
							for z in y:
								if self._isLeaf(z):
									negation = self._negator(self._getLeafTxt(z), negation)
						else:
							negation = self._negator(self._getLeafTxt(y), negation)
				if x.node == "VP" or x.node == 'REQ':
					if self.vb:
						print "NLU: parse_PRP: examining VP nodes"
					for y in x:
						if self._isLeaf(y):
							negation = self._negator(self._getLeafTxt(y), negation)
							verb = self._classify_word(y, self.adjectiveSS_list)
							
							if verb[1] > rating[1] and verb[0] != None:
								rating = [self._determine_rating(verb[0], negation), verb[1]]
								negation = False #reset neg after ea. application
				## END This needs to be changed
				elif x.node == "NP":
					## if node is an NP, that means the chunker couldn't find a movieTitle, Person, or KW.
					## Essentially, We don't know what this is
					## save it as unclassified, as we may get hints later
					## save current state of negation, so we can examine negation and the node at the same time
					unclassifiedEntities.append([negation, x])
					negation = False #reset neg after ea. application
					
				elif x.node == "TITLE":
					entSet.add_entity2("movieTitle", self._getTreeTxt(x), negation, True)
					negation = False #reset neg after ea. application
					
				elif x.node == "PERSON":
					if looking_for == "actor" or looking_for == "director":
						entSet.add_entity2(looking_for, self._getTreeTxt(x), negation, True)
						negation = False #reset neg after ea. application
					else:
						unclassifiedEntities.append([negation, x])
						negation = False #reset neg after ea. application
				elif x.node == "TIME_RANGE":
					for y in x:
						if self._getLeafTos(y) == 'CD':
							entSet.add_entity2('timespan', self._getLeafTxt(y), negation, 'timespan2')
					negation = False ## reset neg after ea. application
			
			## This 'else' catches leafs at main level:
			else:
				tagOfSpeech = self._getLeafTos(x)
				theWord = self._getLeafTxt(x)
				
				negation = self._negator(theWord, negation)
				
				## stage look-forward or look-backward:
				keyword = ""
				if tagOfSpeech == 'KW_DIRECTOR':
					keyword = 'director'
				elif tagOfSpeech == 'KW_STAR':
					keyword = 'actor'
				elif tagOfSpeech == 'KW_GENRE':
					keyword = 'genre'
				elif tagOfSpeech == 'KW_PLOT':
					keyword = 'plot'
				
				if keyword != "":
					looking_for = keyword
					#if classifyUnknowns:
					if len(unclassifiedEntities) > 0:
						## EXE look-backward!
						if self.vb:
							print "NLU: parse_PRP: look-backwards"
						while len(unclassifiedEntities) != 0:
							neg, y = unclassifiedEntities.pop()
							backupName = "other"
							if y.node == "PERSON":
								backupName = "person"
							#print "adding %s as %s with backup %s" % (self._getTreeTxt(y), looking_for, backupName)
							#entSet.add_entity2(looking_for, self._getTreeTxt(y), neg, backupName)
							entSet.add_entity2(looking_for, self._getTreeTxt(y), neg, True)
						classifyUnknowns = False ## switch back to looking-forward
						looking_for = "other" ## reset the looking_for token
				elif tagOfSpeech == 'KW_MOVIE':
					pass ## ignore KW_MOVIE, QUOTES will find the movie
				elif tagOfSpeech == 'GNRE':
					entSet.add_entity2("genre", theWord, negation, True)
				elif theWord.lower() == 'as' and len(unclassifiedEntities) > 0:
					## "AS" is special, in that in labels the NP before it as something
					## If we encounter "AS" and we have unclassified utterances,
					## Try to classify unknowns with keywords that proceed "AS"
					classifyUnknowns = True
				else:
					if theWord.lower() in self.genre_list:
						# If the chunker didn't classify a word with GENRE
						# this should catch it
						entSet.add_entity2("genre", theWord, negation, True)
						negation = False #reset neg after ea. application
					else:
						adj, score = self._classify_word(x, self.adjectiveSS_list)
						if score > rating[1] and adj != None:
							if self.vb:
								print "NLU: '%s'rating REPLACE (%s, %.05f) -> (%s, %.05f)" % (theWord, rating[0], rating[1], adj, score)
						
							rating = [self._determine_rating(adj, negation), score]
							negation = False #reset neg after ea. application
	
		## make sure to add unclassifiedEntities to the EntitySet before returning
		while len(unclassifiedEntities) != 0:
			neg, y = unclassifiedEntities.pop()
			EntityName = "other"
			if y.node == 'PERSON':
				EntityName = "person"
			entSet.add_entity2(EntityName, self._getTreeTxt(y), neg, True)
		

		if rating[1] > 0.25:
			## tolerance level: be 25% sure before adding rating
			entSet.add_entity("rating", rating[0])
		
		return entSet

	def _determine_rating(self, word, negation):
		rating = 3
		if word in self.rating5_list:
			if negation:
				rating = 1
			else:
				rating = 5
		elif word in self.rating4_list:
			if negation:
				rating = 2
			else:
				rating = 4
		elif word in self.rating2_list:
			if negation:
				rating = 4
			else:
				rating = 2
		elif word in self.rating1_list:
			if negation:
				rating = 5
			else:
				rating = 1

		if self.vb:
			print "Called _determine_rating('%s', %s):- %d" % (word, negation, rating)

		return rating

	##	Takes two synsets as arguments and returns a similarity score from 0 to 1.
	def _synset_similarity(self, set1, set2):
		similar_tos = False	
		similarity = 0

		# Iterate over both synsets
		for x in set1:
			for y in set2:
				# Regardless of POS check both entries against their similar_tos()
				# entries. This is particularly helpful for adjectives.
				for z in x.similar_tos():
					for w in y.similar_tos():
						if (y == z) | (w == x):
							similar_tos = True
							break
					if similar_tos: #mission accomplished, break
						break
				
				# If two entries have the same part of speech calculate their path
				# similarity and keep track of the max so far.
				if x.pos == y.pos:
					tmp_sim = x.path_similarity(y)
					if similar_tos:
						tmp_sim *= 1.5 #reward similar tos
					if tmp_sim > similarity:
						similarity = tmp_sim
				similar_tos = False

		# Give similar_tos a score
		#if (similar_tos) & (similarity < .2):
		#	similarity = .35
		
		#if self.vb:
		#	print "similar: %.05f / %.05f" % (similarity, self._OLDsynset_similarity(set1, set2))
		return similarity