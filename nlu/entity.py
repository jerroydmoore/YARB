'''
Created on Feb 2, 2011

@author: yangwookkang
'''

class EntitySet(object):

	def __init__(self, classifier, verbose = False):
		self.classifier = classifier
		self.vb = verbose
		self.entities = {}
	
	def add_entity(self, name, value):
		if self.vb and self.has_entity(name):
			print "Entity Changed '%s': '%s' -> '%s'" % (name, self.find_entity(name), value)
		self.entities[name] = value
	
	def remove_entity(self, name):
		if self.has_entity(name):
			del(self.entities[name])
	
	def find_entity(self, name):
		return self.entities[name]
	
	def has_entity(self, name):
		return self.entities.has_key(name)
	
	def get_entitylist(self):
		return self.entities
	
	def get_entityitems(self):
		return self.entities.iteritems()
	
	def get_classifier(self):
		return self.classifier
	
	def print_entities(self):
		for k, v in self.entities.iteritems():
			print k,v
	
	def count_entities(self):
		return len(self.entities)
	
	def toString(self):
		toStr = self.classifier + ", [ "
		#print ", [ "
		for k, v in self.entities.iteritems():
			#toStr += "(" + k + ", " + v + ") "
			toStr += "(%s, %s) " % (k, v)
			#t = "(%s, %s) " % (k, v)
			#toStr += t
		toStr += "]"
		return toStr
		
	## This more adv add handles negation and a contingency plan if the entity already exists
	def add_entity2(self, name, value, negation, backupName = ''):
		prefix = ""
		if negation:
			prefix = "!"
		name = prefix + name

		if backupName == True and self.has_entity(name):
			itor = 2
			potentialName = name + str(itor)
			while self.has_entity(potentialName):
				itor += 1
				potentialName = name + str(itor)
			name = potentialName
		elif backupName != '' and self.has_entity(name):
			name = prefix + backupName

		self.add_entity(name, value)

	def change_classifier(self, new_classifier):
		self.classifier = new_classifier
	
	def copy(self):
		returnVar = EntitySet(self.get_classifier())
		for k,v in self.get_entityitems():
			returnVar.add_entity(k, v)
		return returnVar
	