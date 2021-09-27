var devices;
function load_devices(){
	var request = new XMLHttpRequest();
	request.open('GET', '/api/device', false);
	request.onload = function() {
		if (request.status >= 200 && request.status < 400) {
			devices = JSON.parse(request.responseText);
		} else {
			console.log('HTTP Error fetching devices')
		}
	}
	request.onerror = function(){
		console.log('Network error during fetching devices')
	}

	request.send()
}

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
console.log(devices)
load_devices();
room_view = rivets.bind(
	document.querySelector('#room'),{
		devices: devices,
		controller: controller,
	}
)
var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('event', function(msg) {
	console.log('Event received', msg);
	if (msg['event'] == 'on' || msg['event'] == 'off'){
		devices.forEach(function update_device(device, index){
			console.log(device['device_id'])
			if (device['device_id'] == msg['device_id']){
				console.log('match')
				if (msg['event'] == 'on'){
					device['device_ison'] = true
				} else {
					device['device_ison'] = false
				}
			}
		});
	}
})
