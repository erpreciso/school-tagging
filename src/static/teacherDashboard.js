$(document).ready(function () {
	newExercise();
	$(".studentName").on("click", function(event){
		var student = event.target.id;
		$.post("/t/askStudentStats", {"student": student});
	});
});

onError = function (){
	askMeRefresh();
	$.get("/channelExpired");
};
onClose = function (){};

newExercise = function (){
	var language = getLanguage(); 
	if (language == "EN") {
		var t1 = "Start Exercise";
		var t2 = "Show Lesson Statistics";
	}
	else if (language == "IT") {
		var t1 = "Inizia un nuovo esercizio";
		var t2 = "Mostra le statistiche della lezione";
	}
	$("#dashboard").before($(document.createElement("button"))
			.attr("id", "startExercise")
			.text(t1)
			.on("click", startExercise));
	$("#dashboard").after($(document.createElement("button"))
			.attr("id", "showStats")
			.text(t2)
			.on("click", function(){$.get("/t/askStats");}));
};

studentStats = function (message) {
	var language = getLanguage();
	if (language == "EN"){
		var t1 = "Correct";
		var t2 = "Wrong";
		var t3 = "Missing";
	}
	else if (language == "IT") {
		var t1 = "Corretti";
		var t2 = "Sbagliati";
		var t3 = "Mancanti";
	}
	var student = message.student;
	var stats = t1 + ": " + message.stats.correct;
	stats += ", " + t2 + ": " + message.stats.wrong;
	stats += ", " + t3 + ": " + message.stats.missing;
	var s = $(document.createElement("div")).text(stats);
	$("#" + student)
		.append(s)
		.css("background-color", "AntiqueWhite")
		.off("click").on("click", function(){
			$(this).children().remove();
			$(this).css("background-color", "transparent");
			$(this).off("click").on("click", function(event){
				var student = event.target.id;
				$.post("/t/askStudentStats", {"student": student});
			});
		});
};

showStats = function (message) {
	var language = getLanguage();
	if (language == "EN"){
		var t1 = "LESSON STATISTICS";
	}
	else if (language == "IT"){
		var t1 = "STATISTICHE DELLA LEZIONE";
	}
	$("#exercise, #answers, #showStats, #studentAnswers").remove();
	var stats = message.stats;
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "stats")
			.text(t1));
	for (name in stats) {
		$("#stats").append($(document.createElement("div"))
				.text(name + ": " + stats[name] + " correct answers"));
	}
};

onMessage = function(message) {
	var language = getLanguage();
	var data = JSON.parse(message.data);
	if (data.type == "studentArrived") {
		var studentName = data.message.studentName;
		var studentsCount = $(".studentName").length;
		var txt = (studentsCount + 1).toString() + ". " + studentName;
		var student = $(document.createElement("div"))
			.attr("id", studentName)
			.addClass("studentName")
			.text(txt)
			.on("click", function(event){
				var student = event.target.id;
				$.post("/t/askStudentStats", {"student": student});
			});
		$("#students").append(student);
	}
	else if (data.type == "studentLogout") {
		$("#" + data.message.studentName).remove();
	}
	else if (data.type == "studentDisconnected") {
		if (language == "EN"){
			var t1 = "It seems I'm offline: ping me...";
			var t2 = ".. or kick me out of the lesson";
		}
		else if (language == "IT"){
			var t1 = "Sembra io sia scollegato: prova a sondare la mia connessione";
			var t2 = "..oppure disconnettimi definitivamente";
		}
		var studentName = data.message.studentName;
		if ($("#" + studentName).children(".pingRequest").length == 0){
			$("#" + studentName).append($(document.createElement("button"))
					.addClass("pingRequest")
					.text(t1)
					.on("click", function(event){
						var student = event.target.parentElement.id;
						$.post("/ping", {"student": student});
					}));
			$("#" + studentName).append($(document.createElement("button"))
					.addClass("logoutStudent")
					.text(t2)
					.on("click", function(event){
						var student = event.target.parentElement.id;
						$.post("/forceLogoutStudent", {"student": student});
					}));
		}
	}
	else if (data.type == "studentAlive") {
		var studentName = data.message.studentName;
		if ($("#" + studentName).children(".pingRequest").length > 0){
			$("#" + studentName).children(".pingRequest").remove();
			$("#" + studentName).children(".logoutStudent").remove();
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
	else if (data.type == "studentStats") {
		studentStats(data.message);
	}
};

function buildExercise(message){
	var language = getLanguage();
	if (language == "EN"){
		var t1 = "EXERCISE";
		var t2 = "OPTIONS";
		var t3 = "Time is up!";
	}
	else if (language == "IT"){
		var t1 = "ESERCIZIO";
		var t2 = "OPZIONI";
		var t3 = "Tempo scaduto!";
	}
	$("#exercise, #answers, #startExercise, #showStats, #stats").remove();
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "exercise")
			.css("font-weight", "bold")
			.text(t1 + ": "));
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "answers")
			.text(t2 + ": "));
	$("#dashboard").after($(document.createElement("button"))
				.attr("id", "timeIsUp")
				.text(t3)
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
						.attr("id", answersProposed[i]["EN"])
						.text(answersProposed[i][language] + " ");
		$("#answers").append(answer);
	}
}

buildDashboard = function (status){
	var language = getLanguage();
	if (language == "EN"){
		var t1 = "STUDENT ANSWERS";
		var t2 = "STATUS BAR";
		var t3 = "Missing";
		var t4 = "All students answered";
	}
	else if (language == "IT"){
		var t1 = "RISPOSTE DEGLI STUDENTI";
		var t2 = "BARRA DI STATO";
		var t3 = "Mancanti";
		var t4 = "Tutti gli studenti hanno risposto";
	}
	cleanDashboard();
	statusBar(status.message.totalAnswers);
	answersGraph(status.message.possibleAnswers);
	function cleanDashboard () {
		$("#studentAnswers, #statusBar").remove();
	};
	function answersGraph(answers){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "studentAnswers")
				.text(t1 + ": "));
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
				.text(t2 + ": "));
		var txt;
		txt = " Answered: "+status.answered.length+" --> "+status.answered;
		$("#statusBar").append($(document.createElement("span"))
				.text(txt));
		if (status.missing.length > 0){
			txt = " " + t3 + ": "+status.missing.length+" --> "+status.missing;
			color = null;
		}
		else {
			txt = " " + t4;
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
	var language = getLanguage();
	if (language == "EN")
		var t1 = " <-- Click on the correct part of the speech";
	else if (language == "IT")
		var t1 = " <-- Clicca sulla corretta parte del discorso";
	if ($("#askValidation").length == 0) {
		$("#timeIsUp").remove();
		$.get("/t/timeIsUp");
		$("#answers").children().css("background-color", "Aqua");
		var instr = $(document.createElement("span"))
			.attr("id", "askValidation")
			.css("background-color", "GreenYellow")
			.text(t1);
		$("#answers").append(instr);
		$("#answers").children().on("click", function (event){
			var valid = event.target.id;
//			var valid = event.target.innerText.trim();
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
