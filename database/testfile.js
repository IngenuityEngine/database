var Database = require('../database')

var db = new Database({coren: {apiRoot:'http://localhost:2020/api/'}}, function(){
	console.log('Database initialzied')
	function findEntities()
	{
		db.find('_entity').execute(function(err, resp)
		{
			console.log('err is', err)
			console.log('resp is', resp)
		})
	}
	setTimeout(findEntities, 6000)
})
