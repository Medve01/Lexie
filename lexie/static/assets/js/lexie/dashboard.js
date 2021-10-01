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

let room_selected = ''

function select_room(){
	console.log('selected')
	console.log(this.value)
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
		console.log(model.rooms[model['%room%']].room_devices[model['%device%']].device_id);
		console.log(model);
		document.forms[model.rooms[model['%room%']].room_devices[model['%device%']].device_id].submit();
	},
	select_room: function(e, model) {
		console.log('selected')
		var args = Array.prototype.slice.call(arguments, 1)
		console.log(args)
		console.log(arguments)
	}
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

room_view = rivets.bind(
	document.querySelector('#room'),{
		rooms: devices,
		controller: controller,
	}
)



// var socket = io.connect('ws://' + document.domain + ':' + location.port, {transports: ['websocket']});
// socket.on('event', function(msg) {
// 	console.log('Event received', msg);
// 	if (msg.event == 'on' || msg.event == 'off'){
// 		devices.forEach(function update_device(device, index){
// 			if (device.device_id == msg.device_id){
// 				if (msg.event == 'on'){
// 					device.device_ison = true;
// 				} else {
// 					device.device_ison = false;
// 				}
// 			}
// 		});
// 	}
// });
