
# Standard modules
import arrow
from datetime import timedelta

# Our modules
import arkInit
arkInit.init()

import tryout
from database import Database
from database import Query

complexQuery = {
	'filter':
		{
			'name': '_entity',
			'formalName': { '$regex': 'tity', '$options': 'i' }
		},
	'select': { 'name': 1, 'description': 1 },
	'sort': { 'name': -1 },
	'limit': 20,
	'skip': 1
}

class test(tryout.TestSuite):

	def setUp(self):
		self.db = Database()
		self.db = self.db.connect()
		self.time = self.db.getTime()
		self.entityQuery = Query('_field', self.time)

	def tearDown(self):
		pass

	def shouldInit(self):
		otherEntityQuery = Query('_entity', self.time)
		self.assertTrue(otherEntityQuery)

	def shouldSelectWthArray(self):
		self.entityQuery.select(['name', 'formalName'])
		self.assertEqual(
			self.entityQuery.selectFields,
			{ 'name' : 1, 'formalName': 1})

	def shouldSortWithArray(self):
		self.entityQuery.sort(['name: desc', 'created'])
		self.assertEqual(
			self.entityQuery.sortFields,
			{ 'name': -1, 'created': 1})

	def shouldGroup(self):
		self.entityQuery.group('link')
		self.assertEqual(
			self.entityQuery.getQueryParams(),
			{
				'filter': {},
				'select': {},
				'sort': {
					'link': 1,
				}
			})

	def shouldGroupAndSort(self):
		self.entityQuery.sort('name').group('link')
		self.assertEqual(
			self.entityQuery.getQueryParams(),
			{
				'filter':{},
				'select':{},
				'sort':
				{
					'link': 1,
					'name': 1
				}
			})

		self.entityQuery.reset()\
			.sort('name')\
			.group('link, dataType')\
			.sort('created')

		self.assertEqual(
			self.entityQuery.getQueryParams(),
			{
				'filter': {},
				'select': {},
				'sort':
				{
					'link': 1,
					'dataType': 1,
					'name': 1,
					'created': 1
				}
			})

	def shouldSortWithFieldandSort(self):
		self.entityQuery.reset().sort('name','desc')
		self.assertEqual(self.entityQuery.sortFields, {
				'name' : -1
			})

	# def shouldQueryNullforDefaultValues(self): #may not be necessary, check again
	# 	self.entityQuery = Query('_field')
	# 	self.entityQuery.reset()
	# 	self.entityQuery.where('editable','is not',True)
	# 	self.assertEqual(self.entityQuery.filters, {
	# 		'editable' : {
	# 			'$nin' : [True, None]
	# 		}
	# 		})

	def shouldReset(self):
		self.entityQuery.reset()
		self.entityQuery.where('editable','is not',True)
		self.entityQuery.reset()
		self.assertEqual(self.entityQuery.filters, {})
		self.assertEqual(self.entityQuery.selectFields,{})
		self.assertEqual(self.entityQuery.sortFields,{})

	def shouldChainSelect(self):
		self.entityQuery = Query('_field', self.time)
		self.entityQuery.select('created').select('name')
		self.assertEqual(self.entityQuery.selectFields,
			{
				'created':1,
				'name': 1
			})

	def shouldSortWithString(self):
		self.entityQuery = Query('_field', self.time)
		self.entityQuery.sort('name:desc formalName')
		self.assertEqual(self.entityQuery.sortFields,
			{
				'name':-1,
				'formalName':1
			})

	def shouldWhereWithIS(self):
		self.entityQuery.where('name','is','_entity')
		self.assertEqual(self.entityQuery.filters,
			{
			'name':'_entity'
			})

	def shouldWhereWithISNOT(self):
		self.entityQuery.where('name','IS NOT','_entity')
		self.assertEqual(self.entityQuery.filters,
			{
				'name':{'$ne': '_entity'}
			})

	def shouldWhereWithIN(self):
		#self.entityQuery.reset()
		self.entityQuery.where('name', 'in', ['_entity', '_field'])
		self.assertEqual(self.entityQuery.filters,
			{
				'name':{ '$in': ['_entity','_field']}
			})

	def shouldWhereWithINasString(self):
		self.entityQuery.where('name','in','_entity, _field')
		self.assertEqual(self.entityQuery.filters,
			{
				'name' :{'$in': ['_entity','_field']}
			})

	def shouldWherewithLESSTHAN (self):
		now = arrow.utcnow().timestamp
		self.entityQuery.where('name','in','_entity, _field') #whyyyy
		self.entityQuery.where('created','less than', now)
		self.assertEqual(self.entityQuery.filters,
			{
				'name': {'$in': ['_entity','_field']},
				'created': {'$lt': now}
			})

	def shouldWhereWithBETWEEN(self):
		dayAgo = (arrow.utcnow() - timedelta(days=1)).timestamp
		now = arrow.utcnow().timestamp
		self.entityQuery.reset().where('created','between',dayAgo,now)
		self.assertEqual(self.entityQuery.filters,
			{
				'created':{
					'$gte': dayAgo,
					'$lte': now
				}
			})

	def shouldWhereWithContains(self):
		self.entityQuery.reset().where('name','contains', 'tity')
		self.assertEqual(self.entityQuery.filters,
			{
				'name':{'$regex': 'tity', '$options': 'i'}
			})

	def shouldWhereWithNOTCONTAINS(self):
		self.entityQuery.reset().where('name','not contains', 'tity')
		self.assertEqual(self.entityQuery.filters,
			{
				'name':{'$regex': '^((?!tity).)*$', '$options':'i'}
			})

	def shouldWhereWithINNEXT(self):
		self.entityQuery.reset().where('created','inNext','1','month')
		self.assertIn('created', self.entityQuery.filters)
		self.assertIn('$gte', self.entityQuery.filters['created'])
		self.assertIn('$lte', self.entityQuery.filters['created'])

	def shouldWhereWithINLAST(self):
		self.entityQuery.reset().where('created','in_last','1','month')
		self.assertIn('created', self.entityQuery.filters)
		self.assertIn('$gte', self.entityQuery.filters['created'])
		self.assertIn('$lte', self.entityQuery.filters['created'])

	def shouldWhereWithINNEXTwithOneM(self):
		self.entityQuery.reset().where('created','inNext','1m')
		self.assertIn('created', self.entityQuery.filters)
		self.assertIn('$gte', self.entityQuery.filters['created'])
		self.assertIn('$lte', self.entityQuery.filters['created'])

	def shouldwherewithinCalendarDay(self):
		self.entityQuery.reset().where('created','inCalendarDay','0')
		self.assertIn('$gte', self.entityQuery.filters['created'])
		self.assertIn('$lte', self.entityQuery.filters['created'])

	def shouldwherewithinCalendarWeek(self):
		self.entityQuery.reset().where('created','inCalendarWeek','0')
		self.assertIn('$gte', self.entityQuery.filters['created'])
		self.assertIn('$lte', self.entityQuery.filters['created'])

	def shouldwherewithinCalendarMonth(self):
		self.entityQuery.reset().where('created','inCalendarMonth','0')
		self.assertIn('$gte', self.entityQuery.filters['created'])
		self.assertIn('$lte', self.entityQuery.filters['created'])

	# shouldmakeObjectIDS from StringIDs not tested as no coren schema

	# def shouldTransformStringListOptionsToNumericEquivalent(self):
	# 	fieldQuery = Query('_field')
	# 	fieldQuery.reset().where('updateMethod','is','manual')
	# 	print('filters here are')
	# 	print(fieldQuery.filters)
	# 	self.assertEqual(fieldQuery.filters,
	# 		{
	# 			'updateMethod': { '$in' : 'manual'}
	# 		})

	#Transform entity names to id equivalents not tested

	# def shouldSetQueryParams(self):
	# 	self.entityQuery.reset().setQueryParams(complexQuery)
	# 	self.assertEqual(self.entityQuery.getQueryParams(), complexQuery)

	def shouldBuildQueryParamsWithNewQuery(self):
		queryParams = self.entityQuery\
			.reset().where('name','is','_entity')\
			.where('formalName','contains','tity')\
			.select('name','description')\
			.sort('name:desc')\
			.limit(20, 1)\
			.getQueryParams()

		print('queryParams:', queryParams)
		print('complexQuery:', complexQuery)
		self.assertEqual(queryParams, complexQuery)

	def shouldPaginate(self):
		queryParams = self.entityQuery.reset().paginate(2).getQueryParams()
		self.assertEqual(queryParams['limit'], Query.defaultPgCount)
		self.assertEqual(queryParams['skip'],(2-1)*Query.defaultPgCount)
		queryParams = self.entityQuery.reset().paginate(4, 30).getQueryParams()
		self.assertEqual(queryParams['limit'],30)
		self.assertEqual(queryParams['skip'],(4-1)*30)

	# should set Query params and convert ids

	# should set query params for field query

# End of test module

if __name__ == '__main__':
	tryout.run(test)
