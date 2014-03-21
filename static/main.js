onOpened = function() {
	//~ alert("HIT");
}
onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "msg") {
		var msg = "<div class='msg'>";
		msg += data.timestamp + " | ";
		msg += data.username + " | ";
		msg += "<strong>" + data.message + "</strong> | ";
		msg += "  ---- ...last message received</div>";
		$("#all_messages").append(msg);
	}
	else if (data.type == "connected user") {
		var user = "<div class='user' id='" + data.username;
		user += "'><div><strong>";
		user += data.role;
		user += "</strong></div><div>";
		user += data.username;
		user += "</div></div>";
		$("#userlist").append(user);
	}
	else if (data.type == "disconnected user") {
		$("#" + data.username).remove();
		//~ alert("disconn " + data.username);
	}
	//~ alert(JSON.stringify(message));
}
