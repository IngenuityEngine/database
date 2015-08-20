// Vendor Modules
/////////////////////////
// var async = require('async')
var Class = require('uberclass')
var debug = require('debug')('shepherd:db_coren')
var _ = require('lodash')



// Our Modules
/////////////////////////
// var helpers = require('coren/shared/util/helpers')
var corenAPI = require('coren/shared/corenAPI')

var corenDatabase = Class.extend({

init: function(options, callback){
	if (_.isFunction(options))
	{
		callback = options
		options = {}
	}
	options = options || {}

	this.keepTrying = options.keepTrying || false

	debug('initialize coren database')

	var self = this
	function initCorenAPI()
	{
		debug('trying to init corenAPI')
		corenAPI.init(options, function(err, coren)
		{
			if (err)
			{
				if (options.keepTrying)
					setTimeout(initCorenAPI, 500)
				else
					throw err
			}
			else
			{
				self.coren = coren
				callback()
			}
		})
	}

	try{
		initCorenAPI()
	}
	catch (err)
	{
		debug('An error with init coren api that was not called back; retrying')
		setTimeout(initCorenAPI, 500)
	}
},
create: function(entityType, data, options, callback)
{
	return this.coren.create(entityType, data, options, callback)
},

find: function(entityType, queryParams, options, callback)
{
	return this.getQuery(this.coren.find(entityType, queryParams, options, callback))
},

update: function(entityType, queryParams, datas, options, callback)
{
	return this.getQuery(this.coren.update(entityType, queryParams, datas, options, callback))
},

remove: function(entityType, queryParams, options, callback)
{
	return this.getQuery(this.coren.remove(entityType, queryParams, options, callback))
},

empty: function(entityType, options, callback)
{
	return this.coren.empty(entityType, options, callback)
},

retryWrap: function(callbackToWrap)
{
	var self = this

	//This helper function simply keeps refiring until it completes successfully
	function tryRequest(onSuccess, onError)
	{
		callbackToWrap(function(err, resp)
		{
			if (err)
				process.nextTick(onError)
			else
				onSuccess(err, resp)
		})
	}

	// This retry function mimics the normal execute() signature
	// except that the second argument here is a keepTrying option
	// which can override the database's default override behavior
	// (which is set by the options given at init)
	function retry(onSuccess, keepTrying)
	{
		if (_.isUndefined(keepTrying))
			keepTrying = self.keepTrying

		if (keepTrying)
			{
				tryRequest(onSuccess, function()
				{
					debug('Failed request, retrying...')
					retry(onSuccess, keepTrying)
				})
			}
		else
			callbackToWrap(onSuccess)
	}

	return retry
},

getQuery: function(query)
{
	// The normal execute is replaced by an execute
	// that takes an optional keepTrying argument after
	// the callback
	// if keepTrying is true, the request will be restarted until
	// it is successful
	query.execute = this.retryWrap(query.execute)
	return query
}

//end of module
})

module.exports = function factory(options, cb)
{
	return new corenDatabase(options, cb)
}