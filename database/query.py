# -*- coding: utf-8 -*-

#pip arrow
#pip python-dateutil
#helpful regexes
#^\t([a-z]+): function\((.+)\)
#\tdef $1(self, $2):

import re
from numbers import Number
import collections
from datetime import timedelta, datetime
import time
import arrow
from dateutil.relativedelta import *
import arkInit
arkInit.init()
import arkUtil


class Query(object):

	defaultSortOrder = 1
	defaultPgCount = 20
	timeEnumMap= {
		'seconds': ['s', 'sec', 'secs', 'second'],
		'minutes': ['m', 'min', 'mins', 'minute', 'minutes'],
		'hours': ['h', 'hr', 'hrs', 'hour', 'hours'],
		'days': ['d', 'day', 'days'],
		'weeks': ['w', 'wk', 'wks', 'week', 'weeks'],
		'months': ['mn', 'mth', 'month', 'months'],
		'years': ['y', 'yr', 'yrs', 'year', 'years'],
	}

	regex_replaceDollarSign = re.compile('\$')
	regex_stripCommas = re.compile(',')
	regex_numbersFromStart = re.compile('^[0-9]+')
	regex_onlyCharacters = re.compile('[A-Za-z]+')
	regex_nonCharacters = re.compile('[^A-Za-z]')

	def __init__(self, entityType, execCallback=None, queryOptions={}):
		self.entityType = entityType
		self.reset()
		self.queryOptions = queryOptions
		if 'data' not in self.queryOptions:
			self.queryOptions['data'] = {}
		self.execCallback = execCallback

		# filter keys are lower case without spaces
		# Not In is transformed to notin when parsed
		self.filterOperatorMap = {
			# Basics
			'is'                : self.filter_equal,
			'isnot'             : self.filter_notEqual,
			'in'                : self.filter_in,
			'all'				: self.filter_all,
			'notin'             : self.filter_notIn,

			# Numbers
			'lessthan'          : '$lt',
			'greaterthan'       : '$gt',
			# range and betweens are inclusive
			'between'           : self.filter_between,
			# not between is exclusive
			'notbetween'        : self.filter_notBetween,

			# Text
			'contains'          : self.filter_contains,
			'notcontains'       : self.filter_notContains,
			'startswith'        : self.filter_startsWith,
			'endswith'          : self.filter_endsWith,

			# Dates
			# ex: ['created','in_next','4 days']
			# ex: ['created','in_next','4','d']
			# second | minute | hour | day | week | month | year
			# s | m | hr | d | w | mn | y
			'innext'           : self.filter_inNext,
			'inlast'           : self.filter_inLast,
			# offset, ex: 0 = today, 1 = tomorrow, -1 = yesterday
			'incalendarday'    : self.filter_inCalenderDay,
			# offset, ex: 0 = self week, 1 = next week, -1 = last week
			'incalendarweek'   : self.filter_inCalendarWeek,
			# offset, ex: 0 = self month, 1 = next month, -1 = last month
			'incalendarmonth'  : self.filter_inCalendarMonth,

			'exists' : self.filter_exists,
			'notexists' : self.filter_notExists,
		}

	def reset(self):
		self.filters = {}
		self.sortFields = {}
		self.groupFields = {}
		self.selectFields = {}
		self.limitVal = None
		self.skipVal = None
		self.queryOptions = {}
		self.incFields = {}

		return self

	# fix: need to be adding through coren fields
	# accepts:
	# 'name','is','_entity'
	# ['name','is','_entity']
	# [['name','is','description'], ['type','is','text']]
	def where(self, *arguments):

		filters = list(arguments)

		if not isinstance(filters[0], list):
			filters = [filters]


		#var field, fullFieldName, operator, valA, valB, filterObj
		compiled = {}
		for queryFilter in filters:
			# full field name is stored so we can do
			# entityType.type or entityType.id
			fullFieldName = queryFilter[0]
			#field = fullFieldName.split('.')[0]

			operator= Query.regex_nonCharacters.sub('',queryFilter[1].lower())
			operator = self.filterOperatorMap[operator]

			if not isinstance(operator, str):
				if len(queryFilter) == 2:
					filterObj = operator(fullFieldName)
				else:
					valA = self.parseInput(queryFilter[2])#, field)
					if (len(queryFilter) == 4):
						valB = self.parseInput(queryFilter[3])#, field)
					else:
						valB = None
					if valB:
						filterObj = operator(fullFieldName,valA,valB)
					else:
						filterObj = operator(fullFieldName, valA)#,valB)
				compiled.update(filterObj)
			else:
				filterObj = {}
				filterObj[operator] = self.parseInput(queryFilter[2])
				compiled[fullFieldName] = filterObj


		self.filters.update(compiled)

		return self


	def _parseSort(self,sort, customOrder=defaultSortOrder):
		customOrder = self.getSortVal(customOrder)
		sorts = self.parseParam(sort, [sort])
		#var field, order, parts
		compiled = {}
		for sort in sorts:
			if ':' in sort:
				parts = sort.split(':')
				field = parts[0].strip()
				order = self.getSortVal(parts[1])
			else:
				field = sort
				order = customOrder

			compiled[field] = order
		#}, self)
		return compiled

	def group(self, group, order=defaultSortOrder):
		compiled = self._parseSort(group, order)
		self.groupFields.update(compiled)
		return self

	# fix: need to be adding through coren fields
	def sort(self, sort, order=defaultSortOrder):
		compiled = self._parseSort(sort, order)
		self.sortFields.update(compiled)
		return self

	def select(self, *arguments):
		selects = self.parseParam(*arguments)
		compiled = {}
		for field in selects:
			compiled[field] = 1
		self.selectFields.update(compiled)

		return self

		#Do these top things

	def limit(self, limit, skip=None):
		self.limitVal = limit
		if isinstance(skip, Number):
			self.skipVal = skip

		return self

	def skip(self, skip):
		self.skipVal = skip

		return self

	def paginate(self, pg, pgCount=defaultPgCount):
		self.limit(pgCount, (pg - 1) * pgCount)

		return self

	def multiple(self, val=True):
		self.queryOptions['multiple'] = val
		return self

	def getQueryParams(self):
		queryParams = {
			'filter': self.filters,
			'select': self.selectFields,
			'sort': self.groupFields
		}

		if self.incFields:
			queryParams['$inc'] = self.incFields

		# group first, then sort
		if self.sortFields:
			self.groupFields.update(self.sortFields)
			queryParams['sort'] = self.groupFields



		if self.limitVal:
			queryParams['limit'] = self.limitVal
		if self.skipVal:
			queryParams['skip'] = self.skipVal

		return queryParams


	def setQueryParams(self, queryParams):
		self.reset()
		self.filters = {}


		for queryFilter in queryParams['filter']:

			fieldName = queryParams['filter'][queryFilter]

			if (queryFilter and '$not' in queryFilter):
				self.filters[fieldName] = {'$not': parsed}
			else:
				self.filters[fieldName] = fieldName #parsed

		self.selectFields = queryParams.select
		self.sortFields = queryParams.sort
		queryParams.limit = int(queryParams.limit, 10)
		if queryParams.limit > 0:
			self.limitVal = queryParams.limit
		queryParams.skip = int(queryParams.skip, 10)
		if queryParams.skip > 0:
			self.skipVal = queryParams.skip

		return self

	def execute(self):
		queryParams = self.getQueryParams()
		return self.execCallback(queryParams, self.queryOptions)

	def set(self, field, val=None):
		if val is None:
			self.queryOptions['data'].update(field)
		else:
			self.queryOptions['data'][field] = val
		return self

	def increment(self, field, val=None):
		if '$inc' not in self.queryOptions['data']:
			self.queryOptions['data']['$inc'] = {}
		self.queryOptions['data']['$inc'][field] = val
		# self.incFields[field] = val
		return self

	def findOne(self):
		self.queryOptions['method'] = 'findOne'
		return self


	def options(self, key, val):
		#var attrs
		# handle both `"key", value` and `{key: value}` -style arguments.
		attrs = {}
		attrs[key] = val

		self.queryOptions.update(attrs)

		return self


	# Removing
	# Filters

	def filter_equal(self, field, valA):
		# in query handles searching for null
		filterObj = {}
		filterObj[field] = valA
		return filterObj

	def filter_notEqual(self, field, valA):
		# in query handles searching for null
		# if self.isDefaultValue(field, valA):
		# 	return self.filter_notIn(field, valA)
		filterObj = {}
		filterObj[field] = {'$ne': valA}
		return filterObj


	def _getInValues(self, field, val):
		if isinstance(val, str):
			val = arkUtil.parseCommaArray(val)
		else:
			val = arkUtil.ensureArray(val)
		val = list(set(val))

		inValues = []
		for v in val:
			dbValue = v
			# multiEntity and multiEntityType fields return
			# an array of objects
			# self lets us sort
			if isinstance(dbValue, list):
				inValues = inValues + dbValue
			else:
				inValues.append(dbValue)
		return inValues

	def filter_in(self, field, valA):
		filterObj = {}
		inValues = self._getInValues(field, valA)

		filterObj[field] = {'$in': inValues}
		return filterObj

	def filter_all(self, field, valA):
		filterObj = {}
		allValues = self.getInValues(field, valA)
		filterObj[field] = {'$all': allValues}
		return filterObj

	def filter_notIn(self, field, valA):
		filterObj = {}
		inValues = self._getInValues(field, valA)
		filterObj[field] = {'$nin': inValues}
		return filterObj

	def filter_between(self, field, valA, valB):
		filterObj = {}
		#valA = arkUtil.ensureNumber(valA)
		#valB = arkUtil.ensureNumber(valB)
		# people pass params in the wrong order
		if valA > valB:
			temp = valA
			valA = valB
			valB = temp
		filterObj[field] = {'$gte':valA, '$lte':valB}
		return filterObj

	def filter_notBetween(self, field, valA, valB):
		filterObj = self.filter_between(field, valA, valB)
		# people pass params in the wrong order
		if valA > valB:
			temp = valA
			valA = valB
			valB = temp
		filterObj[field] = self.notFilter(filterObj[field])
		return filterObj

	def filter_contains(self, field, valA):
		filterObj = {}
		valA = valA.strip()
		regexStr = valA
		filterObj[field] = {'$regex': regexStr, '$options': 'i' }
		return filterObj

	def filter_notContains(self, field, valA):
		filterObj = {}
		valA = valA.strip()
		# (?! is a negative lookahead
		# it matches things not followed by something else
		# self regex matches only if everything is not followed by valA:
		# from the start to the end of the string
		# the period is after the lookahead to prevent strings
		# starting w valA from matching
		regexStr = '^((?!' + valA + ').)*$'
		filterObj[field] = {'$regex': regexStr, '$options': 'i' }
		return filterObj

	def filter_startsWith(self, field, valA):
		filterObj = {}
		valA = valA.strip()
		regexStr = '^' + valA
		filterObj[field] = {'$regex': regexStr, '$options': 'i' }
		return filterObj

	def filter_endsWith(self, field, valA):
		filterObj = {}
		valA = valA.strip()
		regexStr = valA + '$'
		filterObj[field] = {'$regex': regexStr, '$options': 'i' }
		return filterObj

	def filter_inNext(self, field, valA, valB=None):
		start = self.now()
		end = self.getTimeVal(valA, valB)
		return self.filter_between(field, start, end)

	def filter_inLast(self, field, valA, valB=None):
		start = self.getTimeVal(valA, valB)
		end = self.now()
		return self.filter_between(field, start, end)

	def filter_inCalenderDay(self, field, valA):
		valA = arkUtil.ensureNumber(valA)
		# 0 is day to day + 1
		# -1 is day to day -1
		# 1 is day + 1 to day + 2
		# -2 is day + -2 to day + -3
		if valA >= 0:
			valA += 1
		start = (arrow.utcnow().floor('day') + timedelta(days=valA-1)).timestamp
		end = (arrow.utcnow().floor('day') + timedelta(days=valA)).timestamp
		return self.filter_between(field, start, end)

	def filter_inCalendarWeek(self, field, valA):
		valA = arkUtil.ensureNumber(valA)
		if valA >= 0:
			valA += 1

		start = (arrow.utcnow().floor('week') + timedelta(weeks=valA-1)).timestamp
		end = (arrow.utcnow().floor('week') + timedelta(weeks=valA)).timestamp
		return self.filter_between(field, start, end)

	def filter_inCalendarMonth(self, field, valA):
		valA = arkUtil.ensureNumber(valA)
		if valA >= 0:
			valA += 1

		start = (arrow.utcnow().floor('month') + timedelta(days=(valA-1)*30)).timestamp
		end = (arrow.utcnow().floor('month') + timedelta(days=(valA)*30)).timestamp
		return (self.filter_between(field, start, end))

	def filter_exists(self, field):
		filterObj = {}
		filterObj[field] = {'$exists': True}
		return filterObj

	def filter_notExists(self, field):
		filterObj = {}
		filterObj[field] = {'$exists': False}
		return filterObj

	def notFilter(self, queryFilter):
		return {'$not':queryFilter}

	def parseFilter(self, queryFilter, field, fullFieldName):
		if isinstance(queryFilter, str):
			return field.parse(queryFilter, fullFieldName)
		elif isinstance(queryFilter, collections.Iterable) and ('$ne' in queryFilter):
			queryFilter['$ne'] = field.parse(queryFilter['$ne'], fullFieldName)
			return queryFilter

		elif isinstance (queryFilter, collections.Iterable) and \
			 (('$in' in queryFilter) or ('$nin' in queryFilter)):
			key = '$in'
			if '$nin' in queryFilter:
				key = '$nin'
			values = []

			for val in queryFilter[key]:
				parsed = field.parse(val, fullFieldName)
				if isinstance(parsed, list):
					values = values.extend(parsed)
				else:
					values.append(parsed)

			queryFilter[key] = values
		return queryFilter

	def parseTimeVal(self, valA, valB=None):
		# num, unit, timeEnum, match
		# split 1month into
		# num=1
		# unit=month
		if not valB:
			match = self.regex_numbersFromStart.search(valA)
			if not match:
				return
			num = int(match.group(0))
			match = self.regex_onlyCharacters.search(valA)
			if not match:
				return
			unit = match.group(0)

		else:
			unit = valB
			num = int(arkUtil.ensureNumber(valA))


		timeEnum = False
		for val in Query.timeEnumMap:
			if unit in Query.timeEnumMap[val]:
				timeEnum = val
		if not timeEnum:
			return
		return {'unit': timeEnum, 'num': num}

	# deals with dates passed two ways
	# ex: ['created','in_next','4 days']
	# ex: ['created','in_next','4','d']
	def getTimeVal(self, valA, valB=None):
		timeVal = self.parseTimeVal(valA, valB)
		if not timeVal:
			return 0

		now = datetime.utcnow()
		relativeTimeArgs = {timeVal['unit'] : timeVal['num']}
		next = now + relativedelta(**relativeTimeArgs)

		return (arrow.get(next).timestamp)

	# Helpers


	# "heading, body author ,  created"
	# becomes [heading, body, author, created]
	def now(self):
		return int(time.time())

	def parseParam(self, val, *args):
		# if args has multiple values, use that as an array:
		if len(args)>1:
			return list(args)

		if isinstance(val, str):
			strings = Query.regex_stripCommas.sub('', val).split(' ')
			if (args and isinstance(args[0], str)):
				strings.append(args[0])
			return strings
		elif isinstance(val, list):
			return val
		else:
			resultList = list(val)
			return resultList

	def parseInput(self, obj):
		if isinstance(obj, str):
			return Query.regex_replaceDollarSign.sub('$', obj)
		return obj

	# convert sort direction string to actual sort direction
	def getSortVal(self, dirString):
		dirString = str(dirString).lower().strip()[0]
		# a for ascending
		if (dirString == 'a' or dirString == '1'):
			return 1
		return -1


	def decodeSpecialVars(self, val):

		# null comes across as undefined otherwise
		if val is None:
			return '__null__'
		elif not val:
			return '__false__'
		return val