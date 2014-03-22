$(document).ready(function() {
	
	$("#send_message").on("click", send_message);
	$("#ask_exercise").on("click", ask_exercise);
	
	
	});

onOpened = function() {
	//~ alert("HIT");
}

onClose = function() {
	//~ alert("hit");
	//~ ''

}

function word_clicked (event) {
	var triggered = event.target.id;
	var base_color = $("#target #" + triggered).css("background-color");
	$("#target").children().css("background-color", base_color);
	$("#target #" + triggered).css("background-color", "yellow");
}

function send_message() {
	var message = $("input[name*='message']").val();
	$("input[name*='message']").val("");
	$.post("/message", {"message": message});
}

function ask_exercise() {
	$.get("/exercise_request");
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
	else if (data.type == "exercise") {
		$("#exercise").remove();
		var instructions = "<div id='instructions'>Please click on the correct ";
		instructions += data.message["to find"];
		instructions += "</div>";
		
		var target = "<div id='target'>";
		for (var i=0; i < data.message.words.length; i++) {
			target += "<div class='word' id='" + i;
			target += "'>" + data.message.words[i] + "</div> ";
		}
		target += "</div>";
		
		var exercise = "<div id='exercise'>";
		exercise += instructions
		exercise += target
		exercise += "</div>";
		$("#exercise_area").append(exercise);
		$(".word").on("click", word_clicked);
	}
	//~ alert(JSON.stringify(message));
}
