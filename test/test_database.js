
// Vendor Modules
/////////////////////////
var _ = require('lodash')
var async = require('async')

// Our Modules
/////////////////////////
var helpers = require('coren/node_modules/arkutil')
var Database = require('../database/database')


// Passed globals
/////////////////////////
// var globals = helpers.getGlobal('coren_testGlobals')
// var coren = globals.context.coren
// var factory = globals.context.factory
// var dummyResponse = globals.dummyResponse
// var $ = globals.$
var expect = require('expect.js')

// Mocha globals
/////////////////////////
var describe = helpers.getGlobal('describe')

// Tests
/////////////////////////
describe('test/test_database', function()
{

// Client / server tests
/////////////////////////
// test functions for client/server
var it = helpers.getGlobal('it')
// var client = helpers.clientOnly(both)
// var server = helpers.serverOnly(both)

// bail after the first error
this.bail(true)


// Test Variables
/////////////////////////
var options = {
	basics: {
		rootUrl: 'http://127.0.0.1',
		port: 2160,
	},
	coren: {
		apiRoot: '/api',
	}
}

// Tests
/////////////////////////
it('initialize', function(done) {
	new Database(options, function(err, database)
	{
		if (err)
			throw err
		expect(database.create).to.be.ok()
		done()
	})
})

it('CRUD', function(done) {
	var id
	new Database(options, function(err, database)
	{
		function createEntry(callback)
		{
			database.create('settings', {
				key: 'TEST_DatabaseTest',
				settings: {
						cool: true,
					},
				}, null, function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.length).to.be(1)
					expect(resp[0]._id).to.be.ok()
					id = resp[0]._id
					callback()
				})
		}
		function findEntry(callback)
		{
			database
				.find('settings')
				.where('key','is','TEST_DatabaseTest')
				.where('settings','exists')
				.where('_id','is',id)
				.limit(1)
				.fetch(function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.length).to.be(1)
					expect(resp[0].settings.cool).to.be(true)
					callback()
				})
		}
		function updateEntry(callback)
		{
			database
				.update('settings')
				.where('key','is','TEST_DatabaseTest')
				.set('settings',{cool: 12, lame: 9})
				.limit(1)
				.execute(function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.modified).to.be(1)
					callback()
				})
		}
		function removeEntries(callback)
		{
			database
				.remove('settings')
				.where('key','is','TEST_DatabaseTest')
				.multiple(true)
				.execute(function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.modified).to.be.greaterThan(0)
					callback()
				})
		}

		async.series(
			[
				createEntry,
				findEntry,
				updateEntry,
				removeEntries,
			], done)

	})
})

it('increment and push', function(done) {
	var id
	new Database(options, function(err, database)
	{
		function createEntry(callback)
		{
			database.create('test_fields', {
				text: 'TEST_databaseTest',
				number: 4,
				// all _entity's fields
				multiEntity: _.map(
					database.schema._entity._fields,
					'_id'),
				}, null, function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.length).to.be(1)
					expect(resp[0]._id).to.be.ok()
					id = resp[0]._id
					callback()
				})
		}
		function firstCheck(callback)
		{

			database
				.find('test_fields')
				.where('_id','is',id)
				.execute(function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.length).to.be(1)
					expect(resp[0]._id).to.be.ok()
					expect(resp[0].number).to.be(4)
					callback()
				})
		}
		function incrementAndPush(callback)
		{
			database
				.update('test_fields')
				.where('_id','is',id)
				.increment('number', 1)
				.push('multiEntity',
					database.schema._field._fields[0])
				.limit(1)
				.execute(callback)
		}
		function secondCheck(callback)
		{

			database
				.find('test_fields')
				.where('_id','is',id)
				.execute(function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.length).to.be(1)
					expect(resp[0]._id).to.be.ok()
					expect(resp[0].number).to.be(5)
					// fix: no check for multiEntity
					// contents
					callback()
				})
		}
		function removeEntries(callback)
		{
			database
				.remove('test_fields')
				.where('text','is','TEST_databaseTest')
				.multiple(true)
				.execute(function(err, resp)
				{
					console.log('err:', err)
					console.log('resp:', resp)
					expect(resp.modified).to.be.greaterThan(0)
					callback()
				})
		}

		async.series(
			[
				createEntry,
				firstCheck,
				incrementAndPush,
				secondCheck,
				removeEntries,
			], done)
	})
})

// end of tests
})
