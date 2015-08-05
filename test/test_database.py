import os
import sys
import unittest
import json
import requests
import arkInit
arkInit.init()

sys.path.append(os.getcwd().replace('\\','/') + '/../')

from database import Database

class corenTest(unittest.TestCase):


	@classmethod
	def setUp(self):
	 	self.coren = Database('http://localhost:2160/api/')

	def tearDown(self):
		pass

	def test_ShouldFindSingleEntity(self):
		coren = Database('http://127.0.0.1:2160/api/')
		just_a_test = coren.find('_entity').execute()

	def test_shouldError_with_invalidID(self):
		try:
			r = self.coren.find('_entity').where('name','is','_entity').execute()
		#	print(r.text)
		except:
			print('we got here')
			pass

	def test_shouldFindEntity(self):
		test = self.coren.find('_entity')\
			.where('name','is','_field')\
			.execute() #.where('_id','is','557f56c2569214b8134ac4fe').execute()
		self.assertEqual(len(test.json()), 1)
		#self.assertEqual(test.json())
		#dictionary = json.loads(test.json())
		#print(len(dictionary))
		#print(test.text)


	def test_shouldUpdateUser(self):
		test = Database('http://localhost:2160/api/_user/557f785b5fb978e8201ce880')
		test.update('_user', {'name':'othernewName'}).execute()
		# test = self.coren.find('_user').execute()
		originalUsers = len(test.json())
		self.coren.create('_user').execute()
		test = self.coren.find('_user').execute()
		self.assertEqual(len(test.json()), originalUsers+1)
		killUser = Database('http://localhost:2160/api/_user/557f6dbcb091f538194f40f5')
		killUser.remove('_user').execute()
		self.coren.create('_user').execute()
		stuff = killUser.find('_user')

	def test_shouldListEntities(self):
		resp = self.coren.find('_entity').execute()
		self.assertNotEqual(len(resp.json()), 0)

	def test_shouldFindSingleEntity(self):
		resp = self.coren.find('_entity').where('name','is','_entity').execute()
		self.assertEqual(len(resp.json()),1)
		self.assertEqual(resp.json()[0]['name'], '_entity')

	def test_shouldCreateEntity(self):
		resp = self.coren.find('_entity').execute()
		numEntities = len(resp.json())
		self.coren.create('_entity', {'name': 'newstuff'}).execute()
		resp = self.coren.find('_entity').execute()
		self.assertEqual(len(resp.json()), numEntities+1)
		resp = self.coren.find('_entity').where('name','is','newstuff').execute()
		self.assertEqual(len(resp.json()), 1)

	def test_shouldListFields(self):
		resp = self.coren.find('_field').execute()
		self.assertNotEqual(len(resp.json()), 0)

	def test_shouldFindSingleFields(self):
		resp = self.coren.find('_field').execute()
		numFields = len(resp.json())
		resp = self.coren.find('_field').where('formalName','is','Related').execute()
		self.assertTrue(len(resp.json())< numFields)

	def test_shouldCreateEntity(self):
		resp = self.coren.find('_field').execute()
		numEntities = len(resp.json())
		self.coren.create('_field', {'name': 'newstuff'}).execute()
		resp = self.coren.find('_field').execute()
		self.assertEqual(len(resp.json()), numEntities+1)
		resp = self.coren.find('_entity').where('name','is','newstuff').execute()
		self.assertEqual(len(resp.json()), 1)
		_id = resp.json()[0]['_id']


	def test_shouldListUsers(self):
		resp = self.coren.find('_user').execute()
		self.assertNotEqual(len(resp.json()), 0)

	def test_shouldUpdateUser(self):
		resp = self.coren.find('_user').execute()
		searchId = resp.json()[0]['_id']
		self.coren.update('_user', {'password': 'newpassword'}).where('_id','is',searchId).execute()
		resp= self.coren.find('_user').where('id','is',str(searchId)).execute()
		passwordCheck = resp.json()[0]['password']
		self.assertEqual(passwordCheck, 'newpassword')
		self.coren.update('_user',{'password' : 'testarosa'}).where('_id','is',searchId).execute()

	def test_shouldCreateUser(self):
		self.coren.create('_user', {'name': 'NewUser', 'password': 'otherPassword'}).execute()
		resp = self.coren.find('_user').where('name','is','NewUser').execute()
		self.assertEqual(len(resp.json()),1)
		_id = resp.json()[0]['_id']
		self.coren.delete('_user').where('name','is','NewUser').execute()

	def test_shouldFindSingleUsers(self):
		self.coren.create('_user', {'name': 'NewUser', 'password': 'otherPassword'}).execute()
		resp = self.coren.find('_user').where('name','is','Grant Miller').execute()
		self.assertEqual(len(resp.json()), 1)
		resp = self.coren.delete('_user').where('name','is','NewUser').execute()

	def test_shouldDeleteUser(self):
		self.coren.create('_user', {'name': 'toDelete'}).execute()
		resp = self.coren.find('_user').execute()
		numUsers = len(resp.json())
		#self.coren.delete('_user').where('name','is','toDelete').execute()
		resp = self.coren.delete('_user').where('name','is','toDelete').execute()
		resp = self.coren.find('_user').execute()
		self.assertEqual(len(resp.json()), numUsers-1)


	def test_shouldListTestFields(self):
		resp = self.coren.find('test_fields').execute()
		self.assertNotEqual(len(resp.json()), 0)


	def test_shouldFindSingleTestField(self):
		resp = self.coren.find('test_fields').where('text','is','test entityType').execute()
		self.assertEqual(len(resp.json()), 1)

	def test_shouldUpdateTestField(self):
		self.coren.update('test_fields',{'text': 'finalEntity'}).where('text','is','new entityType').execute()
		resp = self.coren.find('')


	def test_shouldCreateTestField(self):
		self.coren.create('test_fields', {'multiEntity': ['stuff', 'more stuff', 'other stuff'], 'text': ' a newly created entityType'}).execute()

	def test_shouldDeleteTestField(self):
		pass



	#def test_shouldIndex


if __name__ == '__main__':
	unittest.main()

