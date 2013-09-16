## This doesn't work: 'TypeError: can't pickle file objects'

import pickle
from nltk.corpus import wordnet as wn

with open('./rating_synsets', 'w') as outfile:

	rating5_list = ['great', 'favorite', 'terrific']
	rating4_list = ['like','good','intellectual','funny', 'fun', 'beautiful']
	rating2_list = ['dislike','bad','stupid','hack','suck']
	rating1_list = ['stupid', 'terrible', 'aweful', 'hate', 'worst']
		
	SS_list = []
	for x in rating5_list:
		SS_list.append((x, wn.synsets(x)))
	for x in rating4_list:
		SS_list.append((x, wn.synsets(x)))
	for x in rating2_list:
		SS_list.append((x, wn.synsets(x)))
	for x in rating1_list:
		SS_list.append((x, wn.synsets(x)))
	
	
	pickle.dump(SS_list, outfile)
	outfile.closed