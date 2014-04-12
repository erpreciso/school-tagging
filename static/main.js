$(document).ready(function() {
	$("#show_html").on("click", loghtml);
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
