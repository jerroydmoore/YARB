class DmOutput:
	def __init__(self, classifier, paging = False, movietitle = ""):
		self.classifier = classifier
		self.paging = paging
		self.items = []
		self.movietitle = movietitle
		self.pages = 1
		self.totalPages = 10
		
	def get_movietitle(self):
		return self.movietitle
		
	def add_listitem(self, item):
		self.items.append(item)
	
	def setPageNumber(self, page):
		self.pages = page
	def getPageNumber(self):
		return self.pages
	def setTotalPages(self, tpage):
		self.totalPages = tpage
	def getTotalPages(self):
		return self.totalPages
		
	def get_items(self):
		return self.items
	
	def get_classifier(self):
		return self.classifier

	def __str__(self):
		return "\n".join(str(v) for v in self.items) 
	
class ListItem(object):

	def __init__(self):
		
		self.entities = {}
	
	def add_entity(self, name, value):
		self.entities[name] = value
	
	def remove_entity(self, name, value):
		self.entities[name] = value
	
	def find_entity(self, name):
		return self.entities[name]
	
	def has_entity(self, name):
		return self.entities.has_key(name)
	
	def get_classifier(self):
		return self.classifier
	
	def print_entities(self):
		for k, v in self.entities.iteritems():
			print k,v 
			
	def __str__(self):
		return " ,".join(str(k) + " " + str(v) for k, v in self.entities.iteritems())
