$(document).ready(function() {
	var role = $("#role").text();
	$("#send_message").on("click", send_message);
	$("#clear_messages").on("click", clear_messages);
	//~ $("#build_dashboard").on("click", build_dashboard);
	if (role == "teacher") {
		build_dashboard();
		get_logged_list();
		get_exercise_list();
	}
	
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
	$.post("/word_clicked", {"word_number": triggered});
}

function sentence_clicked (event) {
	var triggered = event.target.id;
	var base_color = $("#exercise_list #" + triggered).css("background-color");
	$("#exercise_list").children($(".sentence")).css("background-color", base_color);
	$("#exercise_list #" + triggered).css("background-color", "yellow");
	var button = "<button id='select_sentence'>Send exercise</button>";
	$("#select_sentence").remove();
	$("#chosen_sentence").remove();
	$("#working_area").append(button);
	$("#working_area").append("<div id='chosen_sentence'></div>");
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
	$("#exercise_list").remove();
	$("#select_sentence").remove();
	$("#working_area").append("<div id='dashboard'></div>");
	$.post("/exercise_request", {"exercise_number": chosen});
}

function get_logged_list() {
	$.get("/get_logged");
}

function build_student_detail(students_list) {
	$("#student_detail").append(students_list);
	//~ TODO
}

function get_exercise_list() {
	$.get("/exercise_list_request");
}

function build_exercises_list(exercises_list) {
	var exercise = "<div id='exercise_list_title'>List of available exercises</div>";
	for (var i = 0; i < exercises_list.length; i++) {
		exercise += "<div class='sentence' id='" + i;
		exercise += "'>" + exercises_list[i].sentence + "</div> ";
	}
	$("#exercise_list").append(exercise);
	$(".sentence").on("click", sentence_clicked);
}

function build_dashboard() {
	//~ <dashboard>
		//~ <exercise_list>
		//~ <classroom_stats>
		//~ <student_detail>
	var dashboard = document.createElement("div");
	$(dashboard).attr("id", "dashboard");
	var exercise_list = document.createElement("div");
	$(exercise_list)
		.attr("id", "exercise_list")
		.append('<div class="title">Exercise list area</div>');
	var classroom_stats = document.createElement("div");
	$(classroom_stats)
		.attr("id", "classroom_stats")
		.append('<div class="title">Classroom statistics area</div>');
	var student_detail = document.createElement("div");
	$(student_detail)
		.attr("id", "student_detail")
		.append('<div class="title">Student details area</div>');
	$(dashboard).append(exercise_list);
	$(dashboard).append(classroom_stats);
	$(dashboard).append(student_detail);
	
	$("#working_area").append(dashboard);
	
	//~ write the exercise
		//~ the content
		//~ the type, scope
	//~ write the classroom stats
	//~ for each student
		//~ write the student detail
			//~ exercise content (live)
			//~ exercise status (live)
}

function build_student_exercise_ui () {
	//~ write the instructions
	//~ write the exercise
	//~ append on click function to select and send
}

function update_student_detail () {
	//~ update the exercise content area in the student detail dashboard
	//~ update the exercise status
	//~ update the classroom stats
}

function update_classroom_stats () {
		//~ update classroom stats based on input received from a single student
}

function append_message (timestamp, username, message) {
	var msg = "<div class='msg'>";
		msg += timestamp + " | ";
		msg += username + " | ";
		msg += "<strong>" + message + "</strong>";
		msg += "</div>";
		$("#all_messages").append(msg);
}

function clear_message_history () {
	$("#all_messages").empty();
}

function update_connected_users_list (username, role, status) {
	if (status == "connected user") {
		var user = "<div class='user' id='" + username;
		user += "'><div><strong>";
		user += role;
		user += "</strong></div><div>";
		user += username;
		user += "</div></div>";
		$("#userlist").append(user);
	}
	else if (status == "disconnected user") {
		$("#" + username).remove();
	}
}

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "students list") {
		build_student_detail(data.list);
		//~ var dashboard = "<div id='student_list'>";
		//~ for (var i = 0; i < data.list.length; i++) {
			//~ var box = "<div class='student' id='";
			//~ box += data.list[i];
			//~ box += "'>" + data.list[i];
			//~ box += exercise;
			//~ box += "</div>";
			//~ dashboard += box;
		//~ }
		//~ dashboard += "</div>";
		//~ $("#working_area").append(dashboard);
	}
	if (data.type == "msg") {
		append_message(data.timestamp, data.username, data.message);
	}
	else if (data.type == "connected user") {
		update_connected_users_list(
				data.username,
				data.role,
				"connected user");
	}
	else if (data.type == "disconnected user") {
		update_connected_users_list(
				data.username,
				data.role,
				"disconnected user");
	}
	else if (data.type == "exercise") {
		var role = $("#role").text();
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
		if (role == "student") {
			exercise += instructions;
		}
		exercise += target;
		exercise += "</div>";
		$("#working_area").append(exercise);
		if (role == "student") {
			$(".word").on("click", word_clicked);
		}
	}
	else if (data.type == "exercises list") {
		build_exercises_list(data.message);
		//~ $("#exercise_list").remove();
		//~ var exercise = "<div id='exercise_list'>";
		//~ exercise += "<div id='exercise_list_title'>List of available exercises</div>";
		//~ for (var i = 0; i < data.message.length; i++) {
			//~ exercise += "<div class='sentence' id='" + i;
			//~ exercise += "'>" + data.message[i].sentence + "</div> ";
		//~ }
		//~ exercise += "</div>";
		//~ $("#working_area").append(exercise);
		//~ $(".sentence").on("click", sentence_clicked);
		
	}
	else if (data.type == "clear message history") {
		clear_message_history();
	}
	//~ alert(JSON.stringify(message));
}
