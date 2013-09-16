#
# To instantiate a chunker:
#
#		x = chunker.Chunker()
#
# To Chunk:
#
#		x.chunk(string)
#
# Example:
#
# 		import chunker
# 		chk = chunker.Chunker()
# 		chunk_tree = chk.chunk("Who directed \"The Big Lebowski\"?")

import nltk
import pickle

class Chunker:

	def __init__(self, verbose=False):
		self.vb = verbose

		if verbose:
			print "#Initializing chunker:"

		# Define regular expressions for punctuation tags
		tagged_punc = [ (r'\"', ':'), (r'\?', 'QM') ]

		if verbose:
			print "   Loading POS tagged training sentences."

		# Load the tagged training sentences.
		f = open( './nlu/training_sentences', 'r' )
		train_sents = pickle.load(f)
		
		#TODO: eventually pickle this!
		## BEGIN new training sentences
		s = [('List', 'VB'), ('the', 'DT'), ('actors', 'KW_STAR'), ('in', 'IN'), ('movie', 'KW_MOVIE'), ('.', '.')]
		train_sents.append(s)
		s = [('I', 'PRP'), ('like', 'VBS'), ('thrillers', 'GNRE'), ('in', 'IN'), ('movie', 'KW_MOVIE'), ('.', '.')]
		train_sents.append(s)
		s = [('Quiz', 'BYE'), ('.', '.')]
		train_sents.append(s)
		
		#Tell me the cast list of "Inception"
		s = [('Tell', 'VB'), ('me', 'PRP'), ('the', 'DT'), ('cast', 'KW_STAR'), ('of', 'IN'), ('"', ':'), ('Inception', 'NN'), ('"', ':'), ('.', '.')]
		train_sents.append(s)
		
		## END new training sentences
		#train_sents.extend(s)
		
		#for x in train_sents:
		#	print x
		
	
		# Define the tagger.

		if verbose:
			print "   Loading maxent_treebank_pos_tagger."

		_POS_TAGGER = 'taggers/maxent_treebank_pos_tagger/english.pickle'
		t1 = nltk.data.load(_POS_TAGGER)
		if verbose:
			print "   Training custom Unigram Tagger."		
		t2 = nltk.UnigramTagger( train_sents, backoff=t1 )

		if verbose:
			print "   Instantiating tagger object."

		self.tagger = nltk.RegexpTagger( tagged_punc, backoff=t2 )

		# Define a chunking grammar.
		chunk_grammar = r"""
			REQ: {^<PRP>(<MD>|<VBP><RB>)?<V.*><PRP>?<TO>?}
			     {^<MD><PRP>}
			EXISTENTIAL: {^<V.*><EX>}
			COMMAND: {^<REQ>?<RB>?<VB|VBP><PRP>?}
			B-QUESTION: {^<REQ|COMMAND>?(<W.*><VBD|VBN|VBZ|VBP>?|<VBD|VBN|VBZ>)}
							{^<MD><PRP>}
			TITLE: {<:><[^:]*>*<:>}	
			PERSON: {<NNP[S]?>+}
			TIME_RANGE: {<IN><DT>?<KW_YEAR>?<CD>(<TO><DT>?<KW_YEAR>?<CD>)?}
			NP:   {<DT|PRP\$>?<JJ.*>*<NN|NNS>(<POS>?<JJ>*<NN|NNS>)?}
			PP: { <IN><NP> }
			
		"""
			#VP: { <MD>?<[V].*>+<IN|CC>? }
			#B-QUESTION: {^<REQ>?<[W].*|VBD|VBN|VBP|VBZ>}
			#NP:   {<DT|PRP\$>?<JJ>*<NN|NNS|KW_MOVIE|KW_STAR>(<POS>?<JJ>*<NN|NNS>)?}
			#NP:   {<DT|PRP\$>?<JJ>*<NN|NNS><TITLE|KW_GENRE|GNRE|KW_PLOT|KW_MOVIE|KW_STAR>?}
			#ACTOR_IN_MOVIE: {<PERSON><.*>*<IN><TITLE>}
			#S: {<CC><.*>*}
		   	#B-QUESTION: {^<[W].*|VBD|VBN|VBP|VBZ>}
		if verbose:
			print "   Instantiating RegexpParser object."
		
		# Define a regular expression chunker
		self.cp = nltk.RegexpParser(chunk_grammar)

		if verbose:
			print "Chunker Initialized.#"
		

	# Takes a string and returns a chunk tree.
	def chunk(self, sentence):
		# sentence = UNMODIFIED user input

		#tokd = user input converted into a list
		tokd = nltk.word_tokenize(sentence)
		
		#tagged = list of tuplets (word, tag)
		# each element of tokd is tagged
		tagged = self.tagger.tag(tokd)
		
		if self.vb:
			print "TAGGED: "
			print tagged
			print "\n\n"
			
		chunked = self.cp.parse(tagged)
		
		if self.vb:
			print "CHUNKED: "
			print chunked 
			print "\n\n"

		return chunked
