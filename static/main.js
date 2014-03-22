$(document).ready(function() {
	
	$("#send_message").on("click", send_message);
	//~ $("a").click(function(event) {
	  //~ event.preventDefault();
	  //~ onClose();
	  //~ alert(event.target);
		//~ });
	});

onOpened = function() {
	//~ alert("HIT");
}

onClose = function() {
	//~ alert("hit");
	//~ ''

}

function send_message() {
	var message = $("input[name*='message']").val();
	$("input[name*='message']").val("");
	$.post("/message", {"message": message});
	//~ alert(message);
}

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "msg") {
		var msg = "<div class='msg'>";
		msg += data.timestamp + " | ";
		msg += data.username + " | ";
		msg += "<strong>" + data.message + "</strong>";
		//~ msg += " |   ---- ...last message received</div>";
		msg += "</div>";
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
