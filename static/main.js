$(document).ready(function() {
	
	$("#send_message").on("click", send_message);
	$("#clear_messages").on("click", clear_messages);
	$("#ask_exercises_list").on("click", ask_exercises_list);
	
	
	});

onOpened = function() {
	//~ alert("HIT");
}

onClose = function() {
	//~ alert("hit");

}

function word_clicked (event) {
	var triggered = event.target.id;
	var base_color = $("#target #" + triggered).css("background-color");
	$("#target").children().css("background-color", base_color);
	$("#target #" + triggered).css("background-color", "yellow");
}

function sentence_clicked (event) {
	var triggered = event.target.id;
	var base_color = $("#exercise_list #" + triggered).css("background-color");
	$("#exercise_list").children($(".sentence")).css("background-color", base_color);
	$("#exercise_list #" + triggered).css("background-color", "yellow");
	var button = "<button id='select_sentence'>Send exercise</button>";
	$("#select_sentence").remove();
	$("#chosen_sentence").remove();
	$("#exercise_area").append(button);
	$("#exercise_area").append("<div id='chosen_sentence'></div>");
	$("#chosen_sentence")
		.css("display", "none")
		.val(triggered);
	$("#select_sentence").on("click", select_sentence);
}

function send_message() {
	var message = $("input[name*='message']").val();
	$("input[name*='message']").val("");
	$.post("/message", {"message": message});
}

function clear_messages() {
	$.get("/clear_messages");
}

function select_sentence () {
	var chosen = $("#chosen_sentence").val();
	send_exercise_request(chosen);
}

function send_exercise_request(exercise_number) {
	$.post("/exercise_request", {"exercise_number": exercise_number});
}

function ask_exercises_list() {
	$.get("/exercise_list_request");
}

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "msg") {
		var msg = "<div class='msg'>";
		msg += data.timestamp + " | ";
		msg += data.username + " | ";
		msg += "<strong>" + data.message + "</strong>";
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
	}
	else if (data.type == "exercise") {
		//~ TODO if teacher, no instructions and no events, it's just a FYI
		//~ ===============================================================
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
	else if (data.type == "exercises list") {
		$("#exercise_list").remove();
		var exercise = "<div id='exercise_list'>";
		exercise += "<div id='exercise_list_title'>List of available exercises</div>";
		for (var i = 0; i < data.message.length; i++) {
			exercise += "<div class='sentence' id='" + i;
			exercise += "'>" + data.message[i].sentence + "</div> ";
		}
		exercise += "</div>";
		$("#exercise_area").append(exercise);
		$(".sentence").on("click", sentence_clicked);
	}
	else if (data.type == "clear message history") {
		$("#all_messages").empty();
	}
	//~ alert(JSON.stringify(message));
}
