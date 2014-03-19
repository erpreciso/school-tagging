onOpened = function() {
	//~ alert("HIT");
}
onMessage = function(message) {
	var data = JSON.parse(message.data);
	
	var msg = "<div class='msg'>"
	msg += data.timestamp + " | "
	msg += data.username + " | "
	msg += "<strong>" + data.message + "</strong> | "
	msg += "  ---- ...last message received</div>"
	$("#all_messages").append(msg);
	//~ alert(JSON.stringify(message));
}
