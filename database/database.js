// Vendor Modules
/////////////////////////
// var async = require('async')
var Class = require('uberclass')
var debug = require('debug')('shepherd:db_coren')
var _ = require('lodash')
var Query = require('coren/shared/query')


// Our Modules
/////////////////////////
// var helpers = require('coren/shared/util/helpers')
var Database = require('coren/client/database_restful')

var corenDatabase = Class.extend({

init: function(options, callback)
{
	_.bindAll(this, _.functionsIn(this))

	if (_.isFunction(options))
	{
		callback = options
		options = {}
	}
	options = options || {}

	debug('initialize coren database with options', options)
	this.keepTrying = options.keepTrying || false

	debug('initialize coren database')

	var self = this
	function initDatabase()
	{
		debug('trying to init corenAPI')
		var context = {
			options: options
		}
		new Database(context, function(err)
		{
			if (err)
			{
				throw err
				// if (options.keepTrying)
				// 	setTimeout(initDatabase, 500)
				// else
				// 	throw err
			}
			else
			{
				self.database = context.databaseRestful
				callback(null, self)
			}
		})
	}

	try
	{
		initDatabase()
	}
	catch (err)
	{
		throw err
		// debug('An error with init coren api that was not called back; retrying')
		// setTimeout(initDatabase, 500)
	}
},
create: function(entityType, data, options, callback)
{
	this.database.create(entityType, data, options, callback)
},

find: function(entityType, queryParams, options, callback)
{
	return this.createQuery('find', entityType, queryParams, options, callback)
},

update: function(entityType, queryParams, datas, options, callback)
{
	return this.createQuery('update', entityType, queryParams, datas, options, callback)
},

remove: function(entityType, queryParams, options, callback)
{
	return this.createQuery('remove', entityType, queryParams, options, callback)
},

empty: function(entityType, options, callback)
{
	return this.database.empty(entityType, options, callback)
},

// retryWrap: function(callbackToWrap)
// {
// 	var self = this

// 	// This function simply keeps firing until it completes successfully
// 	function tryRequest(successCallback, errCallback)
// 	{
// 		callbackToWrap(function(err, resp)
// 		{
// 			if (err)
// 				process.nextTick(errCallback)
// 			else
// 				successCallback(err, resp)
// 		})
// 	}

// 	// This retry function mimics the normal execute() signature
// 	// except that the second argument here is a keepTrying option
// 	// which can override the database's default override behavior
// 	// (which is set by the options given at init)
// 	function retry(successCallback, keepTrying)
// 	{
// 		if (_.isUndefined(keepTrying))
// 			keepTrying = self.keepTrying

// 		if (keepTrying)
// 		{
// 			tryRequest(successCallback, function()
// 			{
// 				debug('Failed request, retrying...')
// 				retry(successCallback, keepTrying)
// 			})
// 		}
// 		else
// 			callbackToWrap(successCallback)
// 	}

// 	return retry
// },

createQuery: function(funcName, entityType, queryParams, options, callback)
{
	// The normal execute is replaced by an execute
	// that takes an optional keepTrying argument after
	// the callback
	// if keepTrying is true, the request will be restarted until
	// it is successful

	var query = new Query(
			{},
			entityType,
			queryParams,
			options,
			callback
		)
	query.execCallback = this.database[funcName]
		.bind(this.database)
	return query
},

//end of module
})

module.exports = function factory(options, cb)
{
	return new corenDatabase(options, cb)
}
