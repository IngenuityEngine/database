
# Standard modules
import time
import requests
import json


# Our modules
import arkInit
arkInit.init()

import cOS
import arkUtil
from query import Query

import settingsManager
globalSettings = settingsManager.globalSettings()

# https://github.com/IngenuityEngine/coren/wiki/Documentation#rest-implementation
class Database(object):

	timeRefresh = 60

	validApiOptions = [
		'getLinks',
		'undo',
		'multiple',
		]

	def __init__(self, apiRoot=None, keepTrying=False):
		if not apiRoot:
			apiRoot = globalSettings.DATABASE

		self.apiRoot = cOS.ensureEndingSlash(apiRoot)
		self.keepTrying = keepTrying
		self.schema = None

	def connect(self):
		if self.schema:
			return self

		while True:
			try:
				self.schema = None
				response = requests.get(self.apiRoot + '_schema')
				response = response.json()
				response = arkUtil.unicodeToString(response)
				self.schema = response
				self.time = response['_time']
				self.lastTimeCheck = time.time()
				return self
			except Exception as e:
				print e
				if self.keepTrying:
					print 'No connection made yet, trying again.'
					time.sleep(0.5)
				else:
					return None

	def getTime(self):
		if time.time() > self.lastTimeCheck + self.timeRefresh:
			self.connect()
			while True:
				try:
					response = requests.get(
						self.apiRoot + '_time')
					response = int(response)
					return response
				except NotImplementedError:
					raise
				except:
					if self.keepTrying:
						print 'Database hasn\'t responded yet, retrying'
						time.sleep(0.5)
					else:
						return None

		timePassed = time.time() - self.lastTimeCheck
		return self.time + timePassed

	def create(self, entityType, data, callback=None):
		queryOptions = {
			'method': 'create',
			'entityType': entityType,
			'data': data
			}
		callback = callback or self.execute
		return Query(entityType, callback, queryOptions)

	def find(self, entityType, callback=None):
		queryOptions = {
			'method': 'read',
			'entityType': entityType,
			}
		callback = callback or self.execute
		return Query(entityType, callback, queryOptions)

	def update(self, entityType, data=None, callback=None):
		queryOptions = {
			'method': 'update',
			'entityType': entityType
			}
		if data:
			queryOptions['data'] = data
		callback = callback or self.execute
		return Query(entityType, callback, queryOptions)

	def remove(self, entityType, callback=None):
		queryOptions = {
			'method': 'delete',
			'entityType': entityType,
			}
		callback = callback or self.execute
		return Query(entityType, callback, queryOptions)

	def empty(self, entityType):
		queryOptions = {
			'method': 'delete',
			'entityType': entityType
		}
		emptyQuery = Query(entityType, self.execute, queryOptions)
		emptyQuery.multiple(True)
		response = self.execute(emptyQuery.getQueryParams(), emptyQuery.queryOptions)
		return response

	def findOne(self, entityType, callback=None):
		queryOptions = {
			'method': 'findOne',
			'entityType': entityType
		}
		callback = callback or self.execute
		return Query(entityType, callback, queryOptions)

	def getID(self, entityType, callback=None):
		queryOptions = {
			'method': 'getID',
			'entityType': entityType
		}
		callback = callback or self.execute
		return Query(entityType, callback, queryOptions)

	def getIDByName(self, entityType, name):
		queryOptions = {
			'method': 'read',
			'entityType': entityType
		}
		query = Query(entityType, self.execute, queryOptions)
		query = query.where('name', 'is', name)
		response = self.execute(query.getQueryParams(), query.queryOptions)
		try:
			return response[0]['_id']
		except:
			return None

	def getApiOptions(self, options):
		# return {k:options[k] for k in options if k in self.validApiOptions}
		return dict((k, options[k])
			for k in options if k in self.validApiOptions)

	def execute(self, queryParams, queryOptions, keepTrying=None):
		self.connect()
		if keepTrying == None:
			keepTrying = self.keepTrying

		while True:
			try:
				response = self._execute(queryParams, queryOptions)
				return response
			except NotImplementedError:
				raise
			except:
				if keepTrying:
					print 'Database hasn\'t responded yet, retrying'
					time.sleep(0.5)
				else:
					return None

	def _execute(self, queryParams, queryOptions):
		data = {'_query': json.dumps(queryParams)}
		data['_options'] = json.dumps(queryOptions)
		# if ('multi' in queryOptions):
		# 	data['_options']=json.dumps({'multi': queryOptions['multi']})

		if queryOptions['method'] in ['read', 'findOne', 'getID']:
			url = self.apiRoot + queryOptions['entityType']
			response = requests.get(self.apiRoot + queryOptions['entityType'], params=data)

		elif queryOptions['method'] == 'update':
			data.update(queryOptions['data'])
			url = self.apiRoot + queryOptions['entityType']
			response = requests.put(url, json = data)

		elif queryOptions['method'] == 'delete':
			url = self.apiRoot + queryOptions['entityType']
			response = requests.delete(url, data=data)

		elif queryOptions['method'] == 'create':
			data = {
				'_data': queryOptions['data'],
				'_options': self.getApiOptions(queryOptions)
			}
			data = queryOptions['data']
			response =  requests.post(self.apiRoot + queryOptions['entityType'], json=data)

		else:
			raise NotImplementedError('The command method is not one of the supported CRUD methods')

		try:
			response = response.json()
			response = arkUtil.unicodeToString(response)
			if queryOptions['method'] == 'findOne':
				if response:
					response = response[0]
				else:
					response = []
			if queryOptions['method'] == 'getID':
				if response:
					response = response[0]['_id']
				else:
					response = []
		except Exception as err:
			raise err
			# raise Exception('A network error occured; ', response)
		return response



def main():
	while True:
		print 'db connect'
		database = Database('http://127.0.0.1/api', keepTrying=True)
		database.connect()
		print 'exec find'
		print database.find('version').limit(1).execute()
		time.sleep(2)

if __name__ == '__main__':
	main()