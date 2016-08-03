
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

	def shouldNotWorkWithoutAKey(self):
		self.db.key = 'banana'
		resp = self.db.find('_entity')\
			.where('name','is','_field')\
			.execute()
		print 'resp:', resp
		self.assertEqual(resp, None)

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

	# def shouldCreateEntity(self):
	# 	resp = self.db.find('_entity').execute()
	# 	numEntities = len(resp.json())
	# 	self.db.create('_entity', {'name': 'newstuff'}).execute()
	# 	resp = self.db.find('_entity').execute()
	# 	self.assertEqual(len(resp.json()), numEntities+1)
	# 	resp = self.db.find('_entity').where('name','is','newstuff').execute()
	# 	self.assertEqual(len(resp.json()), 1)

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

	# def shouldCreateField(self):
	# 	resp = self.db.find('_field').execute()
	# 	numEntities = len(resp.json())
	# 	self.db.create('_field', {'name': 'newstuff'}).execute()
	# 	resp = self.db.find('_field').execute()
	# 	self.assertEqual(len(resp.json()), numEntities+1)
	# 	resp = self.db.find('_entity').where('name','is','newstuff').execute()
	# 	self.assertEqual(len(resp.json()), 1)
	# 	_id = resp.json()[0]['_id']

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

	# def shouldIncrementTestField(self):
	# 	self.db.create('fields', {'name': 'updateField', 'number': 3}).execute()
	# 	self.db.update('fields')\
	# 				.where('name','is','updateField')\
	# 				.increment('number', 5)\
	# 				.execute()
	# 	result = self.db.findOne('fields')\
	# 						.where('name','is','updateField')\
	# 						.execute()
	# 	self.db.remove('fields')\
	# 				.where('name', 'is', 'updateField')\
	# 				.multiple(True)\
	# 				.execute()
	# 	self.assertEqual(result['number'], 8)



	#def shouldIndex


if __name__ == '__main__':
	tryout.run(test)
