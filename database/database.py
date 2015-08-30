from time import sleep

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
			return

		try:
			self.coren = coren.Coren(self.apiRoot)
			return self
		except:
			if self.keepTrying:
				self.coren = None
				while not self.coren:
					print 'No connection made yet, trying again.'
					sleep(0.5)
					try:
						self.coren = coren.Coren(self.apiRoot)
					except:
						pass
				return self
			else:
				return None
				# return False
				#raise Exception('The database could not be initialized at %s, please check the connection' % self.apiRoot)


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
		try:
			response = self.coren.execute(queryParams, queryOptions)
			return response
		except:
			if keepTrying:
				response = None
				while response == None:
					try:
						print('Database hasn\'t responded yet, retrying')
						sleep(0.5)
						response = self.coren.execute(queryParams, queryOptions)
					except NotImplementedError:
						raise
					except:
						pass
			else:
				raise
