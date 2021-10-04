/* jshint esversion: 6 */
var devices;
function load_devices(){
	var request = new XMLHttpRequest();
	request.open('GET', '/api/device?groupby=rooms', false);
	request.onload = function() {
		if (request.status >= 200 && request.status < 400) {
			devices = JSON.parse(request.responseText);
		} else {
			console.log('HTTP Error fetching devices');
		}
	};
	request.onerror = function(){
		console.log('Network error during fetching devices');
	}

	request.send();
}

function add_room() {
	var request = new XMLHttpRequest();
	room_params = '{"room_name": "' + document.forms.add_room.elements.room_name.value + '"}';
	console.log(room_params);
	request.open('PUT', '/api/room/', false);
	request.onload = function() {
		if (request.status >= 200 && request.status < 400) {
			console.log(request.responseText);
			result = JSON.parse(request.responseText);
		} else {
			console.log('HTTP Error creating room');
		}
	};
	request.send(room_params);
	window.location.reload(true);

}
controller = {
	toggle_relay: function(e, model) {
		var device = model.rooms[model['%room%']].room_devices[model['%device%']];
		console.log('toggle device: ' + device.device_id);
		var request = new XMLHttpRequest();
		request.open('GET', '/api/device/' + device.device_id + '/toggle', false);
		request.onload = function() {
			if (request.status >= 200 && request.status < 400) {
				console.log(request.responseText)
				result = JSON.parse(request.responseText);
			} else {
				console.log('HTTP Error fetching devices');
			}
		}
		request.send();
	},
	move_device: function(e, model) {
		document.forms[model.rooms[model['%room%']].room_devices[model['%device%']].device_id].submit();
	},
	delete_room: function(e, model) {
		room_id = model.rooms[model['%room%']].room_id;
		console.log('Deleting room ' + room_id);
		var request = new XMLHttpRequest();
		request.open('DELETE', '/api/room/' + room_id, false);
		request.onload = function() {
			if (request.status >= 200 && request.status < 400) {
				console.log(request.responseText);
				result = JSON.parse(request.responseText);
			} else {
				console.log('HTTP Error deleting room');
			}
		};
		request.send();
		window.location.reload(true);
	},
	delete_device: function(e, model) {
		device_id = model.rooms[model['%room%']].room_devices[model['%device%']].device_id;
		console.log('Deleting device ' + device_id)
		var request = new XMLHttpRequest();
		request.open('DELETE', '/api/device/' + device_id, false);
		request.onload = function() {
			if (request.status >= 200 && request.status < 400) {
				console.log(request.responseText);
				result = JSON.parse(request.responseText);
			} else {
				console.log('HTTP Error deleting device');
			}
		};
		request.send();
		window.location.reload(true);
	},
}
load_devices();

rivets.components['room-selector'] = {
	template: () => document.getElementById("roomselector-template").innerHTML  ,
	initialize: (el, attrs) => {
		return { data: null };
	  }
  };

rivets.formatters.hashtag = str => {
	return '#'.concat(str);
};

rivets.formatters.modal = function(value, decorator, hashtag) {
	if (hashtag){
		return '#'.concat(value).concat('_').concat(decorator);
	}
	return value.concat('_').concat(decorator);
}

room_view = rivets.bind(
	document.querySelector('#room'),{
		rooms: devices,
		controller: controller,
	}
)



// var socket = io.connect('ws://' + document.domain + ':' + location.port, {transports: ['websocket']});
var socket = io.connect('ws://' + document.domain + ':' + location.port);
socket.on('event', function(msg) {
	console.log('Event received', msg);
	if (msg.event.event_type == 'status'){
		if (msg.event.event_data == 'on' || msg.event.event_data == 'off'){
			devices.forEach(function crawl_rooms(room, index){
				room.room_devices.forEach(function update_device(device, index){
					if (device.device_id == msg.device_id){
						if (msg.event.event_data == 'on'){
							device.device_ison = true;
						} else {
							device.device_ison = false;
						}
					}
				});
			});
		}
	}
});
