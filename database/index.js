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

	debug('initialize coren database')
	corenAPI.init(options, function(err, coren)
	{
		if (err)
			throw err
		this.coren = coren
		callback()
	}.bind(this))
},
create: function(entityType, data, options, callback)
{
	return this.coren.create(entityType, data, options, callback)
},

find: function(entityType, queryParams, options, callback)
{
	return this.coren.find(entityType, queryParams, options, callback)
},

update: function(entityType, queryParams, datas, options, callback)
{
	return this.coren.update(entityType, queryParams, datas, options, callback)
},

remove: function(entityType, queryParams, options, callback)
{
	return this.coren.remove(entityType, queryParams, options, callback)
},

empty: function(entityType, options, callback)
{
	return this.coren.empty(entityType, options, callback)
},

retryWrap: function(callbackToWrap)
{
	function retry(callback)
	{
		try
		{
			callbackToWrap(function(err, resp)
			{
				if (err)
				{
					setTimeout(retry, 500)
					return
				}
				return callback(err, resp)
			})
		}
		catch (err)
		{
			setTimeout(retry, 500)
		}
	}
	return retry
}

//end of module
})

module.exports = function factory(options, cb)
{
	return new corenDatabase(options, cb)
}