$(document).ready(function() {
	var role = $("#role").text();
	$("#send_message").on("click", send_message);
	$("#clear_messages").on("click", clear_messages);
	$("#show_html").on("click", loghtml);
	if (role == "teacher") {
		build_t_dashboard();
		get_logged_list();
		get_exercise_list();
	}
});

onOpened = function() {}

onClose = function() {}

function mylog(message) {
	if (window.console && window.console.log) {
		console.log(message);
	}
}

function loghtml(){
	mylog($("body").html());
}

function word_clicked (event) {
	var triggered = event.target.id;
	var base_color = $("#target #" + triggered).css("background-color");
	$("#target").children().css("background-color", "inherit");
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
	$.get("/dashboard/get_logged");
}

function build_t_student_detail(students_list) {
	for (var i = 0; i < students_list.length; i++) {
		var student_dashboard = $(document.createElement("div"))
			.attr("class", "student_dashboard")
			.attr("id", students_list[i]);
		var name = $(document.createElement("div"))
			.attr("class", "name")
			.text(students_list[i]);
		var exercise_content = $(document.createElement("div"))
			.attr("class", "exercise_content");
		var exercise_status = $(document.createElement("div"))
			.attr("class", "exercise_status");
		var response_time = $(document.createElement("div"))
			.attr("class", "response_time");
		$(student_dashboard)
			.append(name)
			.append(exercise_content)
			.append(exercise_status)
			.append(response_time);
		$("#student_detail").append(student_dashboard);
	}
}

function get_exercise_list() {
	$.get("/dashboard/exercise_list");
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

function build_t_dashboard() {
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
}

function build_ts_exercise (exercise) {
	//~ student UI
	var role = $("#role").text();
	if (role == "student") {
		$("#exercise").remove();
		var instructions = "<div id='instructions'>Please click on the correct ";
		instructions += exercise["to find"];
		instructions += "</div>";
		
		var target = "<div id='target'>";
		for (var i=0; i < exercise.words.length; i++) {
			target += "<div class='word' id='" + i;
			target += "'>" + exercise.words[i] + "</div> ";
		}
		target += "</div>";
		
		var exercise = "<div id='exercise'>";
		exercise += instructions;
		exercise += target;
		exercise += "</div>";
		$("#working_area").append(exercise);
		$(".word").on("click", word_clicked);
	}
	else if (role == "teacher") {
		var param = {"action": "build", "exercise": exercise};
		update_t_student_detail(param);
	}
}

function update_t_student_detail (p) {
	if (p.action == "build") {
		var students = $("#student_detail").children(".student_dashboard");
		for (var i = 0; i < students.length; i++) {
			var words = $(document.createElement("div")).attr("id", "words");
			for (var j=0; j < p.exercise.words.length; j++) {
				var word = $(document.createElement("div"))
					.attr("class", "word")
					.attr("id", j)
					.text(p.exercise.words[j] + " ");
				if (j == p.exercise.answer) {
					$(word)
						.css("font-weight", "bold");
						//~ .attr("class", "correct");
				}
				$(words).append(word);
			}
			var exercise_content = $(document.createElement("div"))
				.attr("class", "exercise")
				.append(words);
			$(students[i]).children(".exercise_content").append(exercise_content);
		}
	}
	else if (p.action == "update") {
		var student = p.content.student;
		var student_dashboard = $("#student_detail #" + p.content.student);
		var triggered = p.content.choice;
		var base = $("#student_detail #" + student + " .exercise .word")
				.css("background-color");
		$("#student_detail #" + student + " .exercise #words")
				.children().css("background-color", "inherit");
		var answer = $("#student_detail #" + student + " .exercise #" + triggered);
		answer.css("background-color", "yellow");
		if (answer.css("font-weight") == "bold") {
			var correct = '<div class="correct">Correct!</div>';
			$("#student_detail #" + student + " .exercise_status")
				.append(correct);
			}
		
		
	}
	//~ update the exercise content area in the student detail dashboard
	//~ update the exercise status
	//~ update the classroom stats
}

function update_t_classroom_stats () {
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
		user += "'><strong>" + username + "</strong></div>";
		$("#userlist").append(user);
	}
	else if (status == "disconnected user") {
		$("#" + username).remove();
	}
}

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "students list") {
		build_t_student_detail(data.list);
	}
	else if (data.type == "student choice") {
		var param = {"action": "update", "content" : data.content};
		update_t_student_detail(param);
	}
	else if (data.type == "msg") {
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
		build_ts_exercise(data.message);
	}
	else if (data.type == "exercises list") {
		build_exercises_list(data.message);
	}
	else if (data.type == "clear message history") {
		clear_message_history();
	}
	//~ alert(JSON.stringify(message));
}
