$(document).ready(function () {
	$("#startExercise").on("click", startExercise);
});

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "student arrived") {
		var studentName = data.message.studentName;
		var studentsCount = $(".studentName").length;
		var txt = (studentsCount + 1).toString() + ". " + studentName;
		var student = $(document.createElement("div"))
			.attr("id", studentName)
			.addClass("studentName")
			.text(txt);
		$("#students").append(student);
	}
	else if (data.type == "student logout") {
		$("#" + data.message.studentName).remove();
	}
	else if (data.type == "session") {
		buildExercise(data.message);
	}
	else if (data.type == "sessionStatus") {
		buildDashboard(data);
	}
};

function buildExercise(message){
	$("#exercise, #answers").remove();
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "exercise")
			.text("EXERCISE: "));
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "answers")
			.text("OPTIONS: "));
	var words = message.wordsList;
	var target = message.target;
	var answersProposed = message.answersProposed;
	for (var i = 0; i < words.length; i++) {
		var word = $(document.createElement("span"))
						.attr("id", words[i])
						.text(words[i] + " ");
		$("#exercise").append(word);
		if (i == target) {
			$(word).css("background-color", "yellow");
		}
	}
	for (var i = 0; i < answersProposed.length; i++ ){
		var answer = $(document.createElement("span"))
			.attr("id", answersProposed[i])
			.text(answersProposed[i] + " ");
		$("#answers").append(answer);
		var par = {"answer": answersProposed[i]};
		$(answer).on("click", par ,function(event){
//			var triggered = event.target.id;
//			$("#" + triggered).css("background-color", "green");
//			$.post("/data/answer", {"answer": triggered});
//			$("#answers").children().off("click");
//			$("#answers").after("Waiting for teacher to assess...");
		});
	}
}

buildDashboard = function (status){
	cleanDashboard();
	statusBar(status.message.totalAnswers);
	answersGraph(status.message.possibleAnswers);
	if ($("#timeIsUp").length == 0) {
		$("#statusBar").after($(document.createElement("button"))
			.attr("id", "timeIsUp")
			.text("Time is up!")
			.on("click", function(){
				alert("hit");
			}));
	}
	
	function cleanDashboard () {
		$("#studentAnswers, #statusBar").remove();
	};
	function answersGraph(answers){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "studentAnswers")
				.text("STUDENT ANSWERS: "));
		for (var answer in answers) {
			var a = $(document.createElement("div"))
					.text(answer.toUpperCase());
			$("#studentAnswers").append(a);
			for (var i = 0; i < answers[answer].length; i++){
				var b = $(document.createElement("div"))
						.text(answers[answer][i]);
				a.append(b);
			}
		}
	}
	function statusBar(status){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "statusBar")
				.text("STATUS BAR: "));
		var t = " Answered: "+status.answered.length+" --> "+status.answered;
		$("#statusBar").append($(document.createElement("span"))
				.text(t));
		t = " Missing: "+status.missing.length+" --> "+status.missing;
		$("#statusBar").append($(document.createElement("span"))
				.text(t));
	}
};

onOpened = function(){};

startExercise = function () {
	$.get("/data/exercise_request");
};

endLesson = function () {
//	viewLessonStats(); //TODO create lesson statistics process
};