import arkInit
arkInit.init()

import coren
import cOS

class Database(object):
	def __init__(self, apiRoot):
		self.apiRoot = apiRoot
		self.coren = coren.Coren(apiRoot)

	def create(self, entityType, data):
		return self.coren.create(entityType, data)

	def find(self, entityType):
		return self.coren.find(entityType)

	def update(self, entityType, data=None):
		return self.coren.update(entityType, data)

	def delete(self, entityType):
		return self.coren.remove(entityType)

	def execute(self, queryParams, queryOptions):
		response = self.coren.execute(queryParams, queryOptions)
		try:
			print('goasdfa here')
			response = cOS.unicodeToString(response.json())
			print('got here')
		except:
			pass
		return response
