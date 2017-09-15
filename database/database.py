
# Standard modules
import os
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
	lastTimeCheck = 0

	validApiOptions = [
		'getLinks',
		'undo',
		'multiple',
		]

	def __init__(self, apiRoot=None, keepTrying=False):
		if not apiRoot:
			apiRoot = globalSettings.DATABASE

		self.key = None
		keyFile = os.environ.get('ARK_CONFIG') + 'key.user.dat'
		try:
			with open(keyFile) as f:
				self.key = f.readlines()[0].strip()
			print 'Using user key'
		except:
			pass

		if not self.key:
			print 'Using default database key'
			keyFile = os.environ.get('ARK_ROOT') + '/ark/config/key.dat'
			try:
				with open(keyFile) as f:
					self.key = f.readlines()[0].strip()
			except Exception as err:
				print 'Could not load default database key'
				raise err

		self.apiRoot = cOS.ensureEndingSlash(apiRoot)
		self.keepTrying = keepTrying
		self.schema = None
		self.health = None

	# Initial connection to database will call database.connect()
	# Afterwards, for .execute() commands, just use health
	def connect(self):
		print 'connecting to :', self.apiRoot
		self.checkHealth()
		return self
		# if self.schema:
		# 	return self

		# while True:
		# 	try:
		# 		self.schema = None
		# 		print 'connecting to :', self.apiRoot + '_schema'
		# 		response = self.get(self.apiRoot + '_schema')
		# 		response = response.json()
		# 		response = arkUtil.unicodeToString(response)
		# 		self.schema = response
		# 		self.getTime()
		# 		return self
		# 	except Exception as e:
		# 		print e
		# 		if self.keepTrying:
		# 			print 'No connection made yet, trying again.'
		# 			time.sleep(0.5)
		# 		else:
		# 			return None

	def checkHealth(self):
		while True:
			try:
				# print 'checking health at :', self.apiRoot + '_health'
				response = self.get(self.apiRoot + '_health')
				response = int(response.json())
				if response is 1:
					return True
			except Exception as e:
				print e
				if self.keepTrying:
					print 'No connection made yet, trying again.'
					time.sleep(0.5)
				else:
					return None

	def getTime(self):
		if time.time() > self.lastTimeCheck + self.timeRefresh:
			while True:
				try:
					response = self.get(self.apiRoot + '_time')
					self.lastTime = int(response.json())
					self.lastTimeCheck = time.time()
					return self.lastTime
				except Exception as e:
					print e
					if self.keepTrying:
						print 'Database hasn\'t responded yet, retrying'
						time.sleep(0.5)
					else:
						return None

		timePassed = time.time() - self.lastTimeCheck
		return self.lastTime + timePassed

	def getQuery(self, entityType, callback, queryOptions):
		return Query(entityType, self.getTime(), callback, queryOptions)

	def create(self, entityType, data, callback=None):
		queryOptions = {
			'method': 'create',
			'entityType': entityType,
			'data': data
			}
		callback = callback or self.execute
		return self.getQuery(entityType, callback, queryOptions)

	def find(self, entityType, callback=None):
		queryOptions = {
			'method': 'read',
			'entityType': entityType,
			}
		callback = callback or self.execute
		return self.getQuery(entityType, callback, queryOptions)

	def update(self, entityType, data=None, callback=None):
		queryOptions = {
			'method': 'update',
			'entityType': entityType
			}
		if data:
			queryOptions['data'] = data
		callback = callback or self.execute
		return self.getQuery(entityType, callback, queryOptions)

	def remove(self, entityType, callback=None):
		queryOptions = {
			'method': 'delete',
			'entityType': entityType,
			}
		callback = callback or self.execute
		return self.getQuery(entityType, callback, queryOptions)

	def empty(self, entityType):
		queryOptions = {
			'method': 'delete',
			'entityType': entityType
		}
		emptyQuery = self.getQuery(entityType, self.execute, queryOptions)
		emptyQuery.multiple(True)
		response = self.execute(emptyQuery.getQueryParams(), emptyQuery.queryOptions)
		return response

	def findOne(self, entityType, callback=None):
		queryOptions = {
			'method': 'findOne',
			'entityType': entityType
		}
		callback = callback or self.execute
		return self.getQuery(entityType, callback, queryOptions)

	def getID(self, entityType, callback=None):
		queryOptions = {
			'method': 'getID',
			'entityType': entityType
		}
		callback = callback or self.execute
		return self.getQuery(entityType, callback, queryOptions)

	def getIDByName(self, entityType, name):
		queryOptions = {
			'method': 'read',
			'entityType': entityType
		}
		query = self.getQuery(entityType, self.execute, queryOptions)
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
		self.checkHealth()
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

	def getCookie(self):
		if self.key:
			return {'oauthToken': self.key}
		return {}

	# wrap request methods w/ getCookie and normalize data name
	def get(self, url, params=None):
		return requests.get(url, params=params, cookies=self.getCookie())

	def put(self, url, data=None):
		return requests.put(url, json=data, cookies=self.getCookie())

	def post(self, url, data=None):
		return requests.post(url, json=data, cookies=self.getCookie())

	# send data as params instead of data, many frameworks strip data from
	# delete requests, namely http-proxy :(
	# https://stackoverflow.com/questions/299628/is-an-entity-body-allowed-for-an-http-delete-request
	def delete(self, url, data=None):
		return requests.delete(url, params=data, cookies=self.getCookie())

	# called on query.execute
	def _execute(self, queryParams, queryOptions):
		data = {'_query': json.dumps(queryParams)}
		data['_options'] = json.dumps(queryOptions)

		if queryOptions['method'] in ['read', 'findOne', 'getID']:
			url = self.apiRoot + queryOptions['entityType']
			response = self.get(self.apiRoot + queryOptions['entityType'], params=data)

		elif queryOptions['method'] == 'update':
			data.update(queryOptions['data'])
			url = self.apiRoot + queryOptions['entityType']
			response = self.put(url, data=data)

		elif queryOptions['method'] == 'delete':
			url = self.apiRoot + queryOptions['entityType']
			response = self.delete(url, data=data)

		elif queryOptions['method'] == 'create':
			data = {
				'_data': queryOptions['data'],
				'_options': self.getApiOptions(queryOptions)
			}
			data = queryOptions['data']
			response =  self.post(self.apiRoot + queryOptions['entityType'], data=data)

		else:
			raise NotImplementedError('The command method is not one of the supported CRUD methods')

		try:
			if response.status_code == 200:
				response = response.json()
				response = arkUtil.unicodeToString(response)
				if queryOptions['method'] == 'findOne':
					if response:
						response = response[0]
					else:
						response = None
				if queryOptions['method'] == 'getID':
					if response:
						response = response[0]['_id']
					else:
						response = None
			else:
				print 'response status:', response.status_code
				raise response.json()
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