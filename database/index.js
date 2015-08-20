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
		console.log('trying to init corenAPI')
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
		console.log('initing corenapi')
		initCorenAPI()
	}
	catch (err)
	{
		console.log('got here')
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

	function retry(onSuccess, keepTrying)
	{
		if (_.isUndefined(keepTrying))
			keepTrying = self.keepTrying

		console.log('retry is ', keepTrying)
		if (keepTrying)
			{
				tryRequest(onSuccess, function()
				{
					console.log('Failed, retrying...')
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
	query.execute = this.retryWrap(query.execute)
	return query
}

//end of module
})

module.exports = function factory(options, cb)
{
	return new corenDatabase(options, cb)
}