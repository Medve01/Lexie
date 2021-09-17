
var devices;
var request = new XMLHttpRequest();
request.open('GET', '/api/device', false);
request.onload = function() {
	if (request.status >= 200 && request.status < 400) {
		// Success!
		// Set items to equal the query results
		console.log(request.responseText)
		devices = JSON.parse(request.responseText);
		// put items.item.condition into items.condition
	} else {
		console.log('HTTP Error fetching devices')
	}
}
request.onerror = function(){
	console.log('Network error during fetching devices')
}

request.send()

controller = {
	toggle_relay: function(e, model) {
		var device = model.devices[model.index]
		console.log('toggle device: ' + device.device_id)
		var request = new XMLHttpRequest();
		request.open('GET', '/api/device/' + device.device_id + '/toggle', false);
		request.onload = function() {
			if (request.status >= 200 && request.status < 400) {
				console.log(request.responseText)
				result = JSON.parse(request.responseText);
			} else {
				console.log('HTTP Error fetching devices')
			}
		}
		request.send()
	}
}
rivets.bind(
	document.querySelector('#room'),{
		devices: devices,
		controller: controller,
	}
)
