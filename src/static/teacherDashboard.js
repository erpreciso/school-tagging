$(document).ready(function () {
	newExercise();
});

newExercise = function (){
	$("#dashboard").before($(document.createElement("button"))
			.attr("id", "startExercise")
			.text("Start Exercise")
			.on("click", startExercise));
	$("#dashboard").after($(document.createElement("button"))
			.attr("id", "showStats")
			.text("Show Lesson Statistics")
			.on("click", function(){$.get("/t/askStats");}));
};

showStats = function (message) {
	$("#exercise, #answers, #showStats, #studentAnswers").remove();
	var stats = message.stats;
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "stats")
			.text("LESSON STATISTICS"));
	for (name in stats) {
		$("#stats").append($(document.createElement("div"))
				.text(name + ": " + stats[name] + " correct answers"));
	}
	
	
};

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "studentArrived") {
		var studentName = data.message.studentName;
		var studentsCount = $(".studentName").length;
		var txt = (studentsCount + 1).toString() + ". " + studentName;
		var student = $(document.createElement("div"))
			.attr("id", studentName)
			.addClass("studentName")
			.text(txt);
		$("#students").append(student);
	}
	else if (data.type == "studentLogout") {
		$("#" + data.message.studentName).remove();
	}
	else if (data.type == "studentDisconnected") {
		var studentName = data.message.studentName;
		if ($("#" + studentName).children(".pingRequest").length == 0){
			$("#" + studentName).append($(document.createElement("button"))
				.addClass("pingRequest")
				.text("It seems I'm offline: ping me...")
				.on("click", function(event){
					var student = event.target.parentElement.id;
					$.post("/ping", {"student": student});
				}));
		}
	}
	else if (data.type == "studentAlive") {
		var studentName = data.message.studentName;
		if ($("#" + studentName).children(".pingRequest").length > 0){
			$("#" + studentName).children(".pingRequest").remove();
		}
	}
	else if (data.type == "sessionExercise") {
		buildExercise(data.message);
	}
	else if (data.type == "sessionStatus") {
		buildDashboard(data);
	}
	else if (data.type == "lessonStats") {
		showStats(data.message);
	}
};

function buildExercise(message){
	$("#exercise, #answers, #startExercise, #showStats, #stats").remove();
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "exercise")
			.css("font-weight", "bold")
			.text("EXERCISE: "));
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "answers")
			.text("OPTIONS: "));
	$("#dashboard").after($(document.createElement("button"))
				.attr("id", "timeIsUp")
				.text("Time is up!")
				.on("click", function(){
					askValidation();
				}));
	var words = message.wordsList;
	var target = message.target;
	var answersProposed = message.answersProposed;
	for (var i = 0; i < words.length; i++) {
		var word = $(document.createElement("span"))
						.text(words[i] + " ");
		$("#exercise").append(word);
		if (i == target) {
			$(word).css("background-color", "yellow");
		}
	}
	for (var i = 0; i < answersProposed.length; i++ ){
		var answer = $(document.createElement("span"))
						.text(answersProposed[i] + " ");
		$("#answers").append(answer);
	}
}

buildDashboard = function (status){
	cleanDashboard();
	statusBar(status.message.totalAnswers);
	answersGraph(status.message.possibleAnswers);
	function cleanDashboard () {
		$("#studentAnswers, #statusBar").remove();
	};
	function answersGraph(answers){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "studentAnswers")
				.text("STUDENT ANSWERS: "));
		for (var answer in answers) {
			var a = $(document.createElement("div"));
			$(a).append($(document.createElement("div"))
					.addClass("title")
					.text(answer.toUpperCase()));
			$("#studentAnswers").append(a);
			for (var i = 0; i < answers[answer].length; i++){
				var b = $(document.createElement("div"))
						.text(answers[answer][i]);
				a.append(b);
			};
		};
	}
	function statusBar(status){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "statusBar")
				.text("STATUS BAR: "));
		var txt;
		txt = " Answered: "+status.answered.length+" --> "+status.answered;
		$("#statusBar").append($(document.createElement("span"))
				.text(txt));
		if (status.missing.length > 0){
			txt = " Missing: "+status.missing.length+" --> "+status.missing;
			color = null;
		}
		else {
			txt = " All students answered";
			color = "YellowGreen";
		}
		var missing = $(document.createElement("span")).text(txt);
		if (color) {$(missing).css("background-color", color);};
		$("#statusBar").append(missing);
	};
};

onOpened = function(){};

startExercise = function () {
	$.get("/data/exercise_request");
};

askValidation = function () {
	if ($("#askValidation").length == 0) {
		$("#timeIsUp").remove();
		$.get("/t/timeIsUp");
		$("#answers").children().css("background-color", "Aqua");
		var instr = $(document.createElement("span"))
			.attr("id", "askValidation")
			.css("background-color", "GreenYellow")
			.text(" <-- Click on the correct part of the speech");
		$("#answers").append(instr);
		$("#answers").children().on("click", function (event){
			var valid = event.target.innerText.trim();
			$("#askValidation").remove();
			$(event.target).css("background-color", "GreenYellow");
			var studentAnswers = $("#studentAnswers").children(); 
			for (var i = 0; i < studentAnswers.length; i++) {
				if ($(studentAnswers[i]).children(".title")[0].innerText 
											== valid.toUpperCase()){
					$(studentAnswers[i]).css("background-color", "GreenYellow");					
				}
			}
			$.post("/data/teacherValidation", {"valid": valid});
			$("#answers").children().off("click");
			newExercise();
		});
	}
};
