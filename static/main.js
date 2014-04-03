$(document).ready(function() {
	var role = $("#role").text();
	$("#show_html").on("click", loghtml);
	if (role == "teacher") {
		build_t_dashboard();
		get_t_logged_list();
		get_t_exercise_list();
	}
});

onOpened = function() {
	$("#connection_status").text("ONLINE")
	.css("color", "green");
	}

onClose = function() {
	$("#connection_status")
		.text("OFFLINE")
		.css("color", "red");
	}

function mylog(message) {
	if (window.console && window.console.log) {
		console.log(message);
	}
}

function loghtml(){
	mylog($("body").html());
}

function send_s_word_clicked (event) {
	var triggered = event.target.id;
	var base_color = $("#target #" + triggered).css("background-color");
	$("#target").children().css("background-color", "inherit");
	$("#target #" + triggered).css("background-color", "yellow");
	$.post("/exercise/word_clicked", {"word_number": triggered});
}

function sentence_t_clicked (event) {
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
	$("#select_sentence").on("click", select_t_sentence);
}

function select_t_sentence () {
	var chosen = $("#chosen_sentence").val();
	//~ $("#exercise_list").remove();
	$("#select_sentence").remove();
	$.post("/dashboard/exercise_request", {"exercise_number": chosen});
	
}

function get_t_logged_list() {
	$.get("/dashboard/get_logged");
}

function update_t_student_dashboards(action, students_list) {
	for (var i = 0; i < students_list.length; i++) {
		if (action == "build") {
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
		else if (action == "remove") {
			$("#" + students_list[0]).remove();
		}
	}
}

function get_t_exercise_list() {
	$.get("/dashboard/exercise_list");
}

function build_t_exercises_list(exercises_list) {
	var exercise = "<div id='exercise_list_title'>List of available exercises</div>";
	for (var i = 0; i < exercises_list.length; i++) {
		exercise += "<div class='sentence' id='" + i;
		exercise += "'>" + exercises_list[i].sentence + "</div> ";
	}
	$("#exercise_list").append(exercise);
	$(".sentence").on("click", sentence_t_clicked);
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
		$(".word").on("click", send_s_word_clicked);
	}
	else if (role == "teacher") {
		var param = {"action": "build", "exercise": exercise};
		update_t_student_detail(param);
		build_t_classroom_stats();
		var button = $(document.createElement("button"))
			.attr("id", "save_and_ask_new")
			.text("Save results and ask new exercise");
		$("#working_area").append(button);
		$(button).on("click", save_and_new_t);
	}
}

function save_and_new_t () {
	//~ create an object to be sent to the server to be stored
	//~ create a new dashboard and a new exercise area
	$("#working_area").empty();
	build_t_dashboard();
	get_t_logged_list();
	get_t_exercise_list();
}

function build_t_classroom_stats() {
	var exercise_status = document.createElement("div");
	$(exercise_status).attr("id", "exercise_status");
	var n = $("#student_detail").children(".student_dashboard").length.toString();
	var students_count_stat = document.createElement("div");
	$(students_count_stat)
		.attr("id", "students_count_stat")
		.text("Students connected: ");
	$(students_count_stat).append('<div id="students_count">' + n + '</div>');
	var respondents_count_stat = document.createElement("div");
	$(respondents_count_stat)
		.attr("id", "respondents_count_stat")
		.text("Students responding: ");
	$(respondents_count_stat).append('<div id="respondents_count">0</div>');
	var winners_count_stat = document.createElement("div");
	$(winners_count_stat)
		.attr("id", "winners_count_stat")
		.text("Students correct: ");
	$(winners_count_stat).append('<div id="winners_count">0</div>');
	$(exercise_status)
		.append(students_count_stat)
		.append(respondents_count_stat)
		.append(winners_count_stat);
	$("#classroom_stats").append(exercise_status);
}

function update_t_logged (n) {
	if ($("#students_count").length > 0) {
		var logged = Number($("#students_count").text());
		logged += n;
		$("#students_count").text(logged);
	}
}

function update_t_respondents (n) {
	if ($("#respondents_count").length > 0) {
		var respondents = Number($("#respondents_count").text());
		respondents += n;
		$("#respondents_count").text(respondents);
	}
}

function update_t_winners (n) {
	if ($("#winners_count").length > 0) {
		var winners = Number($("#winners_count").text());
		winners += n;
		$("#winners_count").text(winners,toString());
	}
}

function update_t_student_detail (p) {
	if (p.action == "build") {
		var students = $("#student_detail").children(".student_dashboard");
		for (var i = 0; i < students.length; i++) {
			$(students[i]).children(".exercise_content").empty();
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
		if ($("#student_detail #" + student + " .exercise_status")
												.children().length == 0) {
				update_t_respondents(1);
				var responding = '<div class="responding">responding...</div>';
				$("#student_detail #" + student + " .exercise_status")
					.append(responding);
				}
		if (answer.css("font-weight") == "bold") {
			if ($("#student_detail #" + student + " .exercise_status")
								.children(".responding").length > 0) {
				$("#student_detail #" + student + " .exercise_status")
					.children(".responding").remove();
				}
			if ($("#student_detail #" + student + " .exercise_status")
								.children(".correct").length == 0) {
				update_t_winners(1);
				var correct = '<div class="correct">Correct!</div>';
				$("#student_detail #" + student + " .exercise_status")
					.append(correct);
				}
			}
		
		
	}
}


function update_ts_connected_users_list (username, role, status) {
	if (role != "teacher") {
		if (status == "connected user") {
			var user = "<div class='user' id='logged_" + username;
			user += "'><strong>" + username + "</strong></div>";
			$("#userlist").append(user);
			update_t_logged(1);
		}
		else if (status == "disconnected user") {
			$("#logged_" + username).remove();
			update_t_logged(-1);
		}
	}
}

onMessage = function(message) {
	var data = JSON.parse(message.data);
	var role = $("#role").text();
	if (data.type == "students list") {
		update_t_student_dashboards("build", data.list);
	}
	else if (data.type == "student choice") {
		var param = {"action": "update", "content" : data.content};
		update_t_student_detail(param);
	}
	else if (data.type == "connected user") {
		update_ts_connected_users_list(
				data.username,
				data.role,
				"connected user");
		if (role == "teacher") {
			update_t_student_dashboards("build", [data.username]);
		}
	}
	else if (data.type == "disconnected user") {
		update_ts_connected_users_list(
				data.username,
				data.role,
				"disconnected user");
		if (role == "teacher") {
			update_t_student_dashboards("remove", [data.username]);
		}
	}
	else if (data.type == "exercise") {
		build_ts_exercise(data.message);
	}
	else if (data.type == "exercises list") {
		build_t_exercises_list(data.message);
	}
	//~ alert(JSON.stringify(message));
}
