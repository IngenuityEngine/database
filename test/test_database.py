
import time

import arkInit
arkInit.init()

import tryout
from database import Database

import settingsManager
globalSettings = settingsManager.globalSettings()
database = Database()

class test(tryout.TestSuite):

	title = 'test/test_database.py'

	def setUp(self):
	 	self.db = Database()
		self.db = self.db.connect()

	def tearDown(self):
		pass

	def shouldCheckHealth(self):
		self.assertEqual(self.db.checkHealth(), True)

	def shouldHaveAKey(self):
		print self.db.key
		self.assertTrue(self.db.key != None)
		self.assertTrue('\n' not in self.db.key)

	# Note: This test will not pass with auth on coren/caretaker
	# def shouldNotWorkWithoutAKey(self):
	# 	self.db.key = 'banana'
	# 	resp = self.db.find('_entity')\
	# 		.where('name','is','_field')\
	# 		.execute()
	# 	print 'resp:', resp
	# 	self.assertEqual(resp, None)

	def shouldFindEntity(self):
		resp = self.db.find('_entity')\
			.where('name','is','_field')\
			.execute()
		self.assertEqual(len(resp), 1)

	def shouldListEntities(self):
		resp = self.db.find('_entity').execute()
		self.assertTrue(len(resp) > 0)

	def shouldFindSingleEntity(self):
		resp = self.db\
			.find('_entity')\
			.where('name','is','_entity')\
			.execute()
		self.assertEqual(len(resp), 1)
		self.assertEqual(resp[0]['name'], '_entity')

	def should_find_with_limit(self):
		entities = self.db.find('_entity').limit(1).execute()
		self.assertTrue(len(entities) == 1)

	def shouldListFields(self):
		resp = self.db.find('_field').execute()
		self.assertTrue(len(resp) > 0)

	def shouldFindSingleFields(self):
		resp = self.db.find('_field').execute()
		numFields = len(resp)
		resp = self.db\
			.find('_field')\
			.where('formalName','is','Related')\
			.execute()
		self.assertTrue(len(resp) < numFields)

	def shouldHaveTime(self):
		timeA = self.db.getTime()
		print 'timeA:', '%d' % timeA
		self.assertTrue(timeA != 0)
		time.sleep(3)
		timeB = self.db.getTime()
		print 'timeB:', '%d' % timeB
		self.assertTrue(timeB > timeA + 2)

	def shouldCreateAnEntry(self):
		resp = self.db.create('test_fields',{'text': 'banana'}).execute()
		self.assertTrue(resp[0]['_id'] is not None)

	def shouldUpdateAnEntry(self):
		self.db.remove('test_fields').multiple().execute()
		og = self.db.create('test_fields',{'text': 'taco'}).execute()
		self.db.create('test_fields',{'text': 'robot'}).execute()
		resp = self.db\
			.update('test_fields')\
			.where('_id','is',og[0]['_id'])\
			.set('text','jungle')\
			.execute()
		print 'resp:', resp
		self.assertEqual(resp['modified'], 1)
		found = self.db.find('test_fields').where('text','is','jungle').execute()
		print 'found:', found
		self.assertEqual(found[0]['_id'], og[0]['_id'])

	def findNotEqual(self):
		result = self.db\
			.remove('test_fields')\
			.where('text','is','testarosa')\
			.multiple()\
			.execute()
		print 'removed:', result['modified']

		self.db.create('test_fields', {'text': 'testarosa'}).execute()
		keeper = self.db.create('test_fields', {'text': 'testarosa'}).execute()
		result = self.db\
			.remove('test_fields')\
			.where('_id','is not',keeper[0]['_id'])\
			.where('text', 'is', 'testarosa')\
			.multiple()\
			.execute()
		print 'result:', result
		self.assertEqual(result['modified'], 1)

	def removeMultiple(self):
		data = [{'count': 12}] * 5

		result = self.db\
			.create('test_fields', data)\
			.execute()
		print 'created:', result

		result = self.db.remove('test_fields')\
			.where('count','is',12)\
			.multiple()\
			.execute()
		self.assertTrue(result['modified'] >= 5)

	def findByID(self):
		data = {'count': 84}

		result = self.db\
			.create('test_fields', data)\
			.execute()

		result = self.db.findOne('test_fields')\
			.where('_id','is',result[0]['_id'])\
			.execute()

		self.assertEqual(result['count'], 84)

	def removeByNameID(self):
		result = self.db\
			.remove('test_fields')\
			.multiple()\
			.execute()

		data = [
			{'name': 'tacos'},
		]

		result = self.db\
			.create('test_fields', data)\
			.execute()

		print 'create:', result

		result = self.db.remove('test_fields')\
			.where('name','is','tacos')\
			.where('_id','is not',result[0]['_id'])\
			.multiple()\
			.execute()

		print result
		self.assertEqual(result['modified'], 0)

	def removeWithComplexQuery(self):

		data = [{'count': 12,'number':8}] * 5

		result = self.db\
			.create('test_fields', data)\
			.execute()

		result = self.db\
			.remove('test_fields')\
			.where('count','is',12)\
			.where('number','is',8)\
			.where('create','in last','2','days')\
			.multiple()\
			.execute()

		print result
		self.assertTrue(result['modified'] > 4)


	# def shouldListUsers(self):
	# 	resp = self.db.find('user').execute()
	# 	self.assertNotEqual(len(resp), 0)

	# def shouldUpdateUser(self):
	# 	resp = self.db.find('user').execute()
	# 	searchId = resp[0]['_id']
	# 	self.db.update('user', {'password': 'newpassword'}).where('_id','is',searchId).execute()
	# 	resp= self.db.find('user').where('id','is',str(searchId)).execute()
	# 	passwordCheck = resp[0]['password']
	# 	self.assertEqual(passwordCheck, 'newpassword')
	# 	self.db.update('user',{'password' : 'testarosa'}).where('_id','is',searchId).execute()

	# def shouldCreateUser(self):
	# 	self.db.empty('user')
	# 	self.db.create('user', {'name': 'NewUser', 'password': 'otherPassword'}).execute()
	# 	resp = self.db.find('user').where('name','is','NewUser').execute()
	# 	self.assertEqual(len(resp),1)
	# 	_id = resp[0]['_id']
	# 	self.db.remove('user').where('name','is','NewUser').multiple(True).execute()

	# def shouldFindSingleUsers(self):
	# 	self.db.create('user', {'name': 'NewUser', 'password': 'otherPassword'}).execute()
	# 	resp = self.db.find('user').where('name','is','NewUser').execute()
	# 	self.assertEqual(len(resp), 1)
	# 	resp = self.db.remove('user').where('name','is','NewUser').execute()

	# def shouldDeleteUser(self):
	# 	self.db.create('user', {'name': 'toDelete'}).execute()
	# 	resp = self.db.find('user').execute()
	# 	numUsers = len(resp)
	# 	#self.db.remove('user').where('name','is','toDelete').execute()
	# 	resp = self.db.remove('user').where('name','is','toDelete').execute()
	# 	resp = self.db.find('user').execute()
	# 	self.assertEqual(len(resp), numUsers-1)

	# def shouldFindSingleTestField(self):
	# 	self.db.create('fields', {'text': 'test entityType'})
	# 	resp = self.db.find('fields').where('text','is','test entityType').execute()
	# 	print(resp.json())
	# 	self.assertEqual(len(resp.json()), 1)
	# def shouldUpdateTestField(self):
	# 	self.db.update('fields',{'text': 'finalEntity'}).where('text','is','new entityType').execute()
	# 	resp = self.db.find('')


	# def shouldCreateTestField(self):
	# 	self.db.create('fields', {'multiEntity': ['stuff', 'more stuff', 'other stuff'], 'text': ' a newly created entityType'}).execute()
	# 	self.db.remove('fields').multiple(True).execute()

	def shouldIncrementTestField(self):
		self.db.empty('test_fields')

		one = self.db.create('test_fields', {'name': 'updateField', 'number': 3}).execute()
		two = self.db.create('test_fields', {'name': 'updateField', 'number': 3}).execute()

		self.db.update('test_fields')\
					.where('_id','in',[two[0]['_id']])\
					.increment('number', 5)\
					.execute()

		result = self.db.findOne('test_fields')\
							.where('_id','is',two[0]['_id'])\
							.execute()

		result = self.db.findOne('test_fields')\
							.where('_id','is',one[0]['_id'])\
							.execute()

		self.assertEqual(result['number'], 3)

		result = self.db.findOne('test_fields')\
							.where('_id','is',two[0]['_id'])\
							.execute()

		self.assertEqual(result['number'], 8)

		self.db.empty('test_fields')



	#def shouldIndex


if __name__ == '__main__':
	tryout.run(test)
