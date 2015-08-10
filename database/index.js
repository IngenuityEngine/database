
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

module.exports = Class.extend({

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
	console.log('entityType is', entityType)
	console.log(queryParams, datas, options)
	return this.coren.update(entityType, queryParams, datas, options, callback)
},

remove: function(entityType, queryParams, options, callback)
{
	return this.coren.remove(entityType, queryParams, options, callback)
},

empty: function(entityType, options, callback)
{
	return this.coren.empty(entityType, options, callback)
}

//end of module
})