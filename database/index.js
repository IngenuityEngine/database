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

	var self = this
	function initCorenAPI()
	{
		console.log('trying to init corenAPI')
		corenAPI.init(options, function(err, coren)
		{
			if (err)
				setTimeout(initCorenAPI, 500)
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
	return function wrappedExecute()
	{
		var ogExecute = callbackToWrap
		console.log('ogExecute:', ogExecute)
		var ogCallback = arguments[arguments.length - 1]
		function run()
		{
			console.log('running')
			ogExecute.apply(arguments)
		}
		function wrappedCallback()
		{
			console.log('wrpaper')
			var err = arguments[0]
			if (err)
			{

			console.log('err')
				setTimeout(wrappedExecute, 500)
			}
			else
			{
			console.log('win')
				ogCallback(arguments)

			}
		}
		console.log('run')
		arguments[arguments.length - 1] = wrappedCallback
		run()
	}































	// return function retry()
	// {
	// 	console.log('ogArguments are', arguments)
	// 	var ogCallback = arguments[arguments.length -1]

	// 	ogExecute(arguments)

	// 	var err = arguments[0]
	// 	if (err)
	// 		return setTimeout(retry(arguments), 500)
	// 	else
	// 		ogCallback(arguments)
		// try
		// {
		// 	var retryingCallback = function(err, resp)
		// 	{
		// 		if (err)
		// 		{
		// 			console.log('oh my god an eerror was found!')
		// 			throw err
		// 		}
		// 		else
		// 			ogCallback(err, resp)
		// 	}
		// 	if (ogArguments.length !== 0)
		// 		ogArguments[ogArguments.length - 1] = retryingCallback
		// 	else
		// 		ogArguments[0] = retryingCallback

		// 	console.log('now ogArguments have turned into ', JSON.stringify(ogArguments))
		// 	callbackToWrap.apply(this, ogArguments)
		// }
		// catch (err)
		// {
		// 	console.log('retrying')
		// 	setTimeout(retry, 500)
		// }
	// }
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