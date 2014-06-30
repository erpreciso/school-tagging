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
		//~ console.log("hit");
		$("#" + data.message.studentName).remove();
	}
	else if (data.type == "session") {
//		add exercise to dashboard
		$("#exercise, #answers").remove();
		$("#startExercise").after($(document.createElement("div"))
				.attr("id", "exercise"));
		$("#exercise").after($(document.createElement("div"))
				.attr("id", "answers"));
		var words = data.message.wordsList;
		var target = data.message.target;
		var answersProposed = data.message.answersProposed;
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
//				var triggered = event.target.id;
//				$("#" + triggered).css("background-color", "green");
//				$.post("/data/answer", {"answer": triggered});
//				$("#answers").children().off("click");
//				$("#answers").after("Waiting for teacher to assess...");
			});
		}
	}
	else if (data.type == "student answer") {
		console.log(data.message);
	}
	else if (data.type == "sessionStatus") {
		console.log(data.message);
//		TODO build graphic dashboard
	}
};

function buildDashboard(answers){
	
	
};

onOpened = function(){};

startExercise = function () {
	$.get("/data/exercise_request");
};
