import time

import arkInit
arkInit.init()

import coren

class Database(object):
	def __init__(self, apiRoot, keepTrying=False):
		self.apiRoot = apiRoot
		self.keepTrying = keepTrying
		self.coren = None

	def connect(self):
		if self.coren:
			# print 'Already have coren'
			return self

		while True:
			try:
				# print 'Trying to get a coren'
				self.coren = coren.Coren(self.apiRoot)
				# print 'returning self'
				return self
			except Exception as e:
				print e
				# print 'coren:', self.coren
				# print 'keepTrying:', self.keepTrying
				if self.keepTrying:
					print 'No connection made yet, trying again.'
					time.sleep(0.5)
				else:
					# print 'returning None'
					return None

	def create(self, entityType, data):
		self.connect()
		return self.coren.create(entityType, data, self.execute)

	def find(self, entityType):
		self.connect()
		return self.coren.find(entityType, self.execute)

	def update(self, entityType, data=None):
		self.connect()
		return self.coren.update(entityType, data, self.execute)

	def remove(self, entityType):
		self.connect()
		return self.coren.remove(entityType, self.execute)

	def empty(self, entityType):
		self.connect()
		return self.coren.empty(entityType)

	def findOne(self, entityType):
		self.connect()
		return self.coren.findOne(entityType)

	def getID(self, entityType):
		self.connect()
		return self.coren.getID(entityType, self.execute)

	def getIDByName(self, entityType, name):
		self.connect()
		return self.coren.getIDByName(self, entityType, name)

	def execute(self, queryParams, queryOptions, keepTrying=None):
		self.connect()
		if keepTrying == None:
			keepTrying = self.keepTrying

		while True:
			try:
				response = self.coren.execute(queryParams, queryOptions)
				return response
			except NotImplementedError:
				raise
			except:
				if keepTrying:
					print 'Database hasn\'t responded yet, retrying'
					time.sleep(0.5)
				else:
					return None



def main():
	while True:
		print 'db connect'
		database = Database('http://127.0.0.1:2020/api', keepTrying=True)
		database.connect()
		print 'exec find'
		print database.find('version').limit(1).execute()
		time.sleep(2)





if __name__ == '__main__':
	main()
