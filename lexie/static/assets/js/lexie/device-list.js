

function setupevents(device_id){
    console.log('Setting up events for device ' + device_id)
    var request = new XMLHttpRequest();
    request.open('GET', '/api/device/' + device_id + '/setup-events', false);
    request.onload = function() {
        if (request.status >= 200 && request.status < 400) {
            // Success!
            // Set items to equal the query results
            console.log(request.responseText)
            devices = JSON.parse(request.responseText);
            // put items.item.condition into items.condition
        } else {
            console.log('HTTP Setting up events')
        }
    }
    request.onerror = function(){
        console.log('Network error during events setup')
    }
    
    request.send()
}
