$(document).ready(function () {
	initializeDashboard();
});

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "sessionExercise")
		presentExercise(data.message);
	else if (data.type == "validAnswer")
		feedbackFromTeacher(data.message);
	else if (data.type == "lessonTerminated")
		lessonTerminated();
	else if (data.type == "pingFromTeacher") {
		console.log(data);
		$.post("/ping", {"alive": true});
	}
	else if (data.type == "sessionExpired") {
		var feedback = "Session aborted by teacher; correct answer was " +
										data.message.validAnswer;
		$("#feedback").text(feedback)
				.css("background-color", "LightGoldenRodYellow ");
	}
};

function lessonTerminated () {
	$("#lessonName").text("Lesson terminated by teacher");
	$("#exercise, #answers").remove();
	if ($("#feedback").length > 0){
		$("#feedback").remove();
	}
}
function presentExercise(message) {
	{
		$("#exercise, #answers").empty();
		if ($("#feedback").length > 0){
			$("#feedback").remove();
		}
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
				.css("background-color", "Moccasin")
				.text(answersProposed[i] + " ");
			$("#answers").append(answer);
			var par = {"answer": answersProposed[i]};
			$(answer).on("click", par ,function(event){
				var triggered = event.target.id;
				$("#" + triggered).css("background-color", "green");
				$.post("/data/answer", {"answer": triggered});
				$("#answers").children().off("click");
			});
		}
		var feedback = $(document.createElement("div"))
			.attr("id", "feedback")
			.text("Waiting for teacher to assess...");
		$("#answers").after(feedback);
	}
}

function feedbackFromTeacher(message) {
	{
		var feedback;
		var background;
		if (message.validAnswer == message.myAnswer){
			feedback = "Good job!";
			background = "GreenYellow";
		}
		else {
			feedback = "Answer not correct; it was " + message.validAnswer;
			background = "Red";
		}
		$("#feedback").text(feedback).css("background-color", background);
	}
}

onOpened = function(){};

function initializeDashboard(){
	$("#lessonName").after($(document.createElement("div"))
			.attr("id", "exercise")
			.text("Waiting for exercise to start..."));
	$("#exercise").after($(document.createElement("div"))
			.attr("id", "answers"));
};
