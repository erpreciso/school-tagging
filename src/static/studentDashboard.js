$(document).ready(function () {
	
	
});

onMessage = function(message) {
	var data = JSON.parse(message.data);
//	TODO split into functions
	if (data.type == "session") {
		$("#exercise, #answers").empty();
		if ($("#feedback").length > 0){
			$("#feedback").remove();
		}
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
	else if (data.type == "validAnswer"){
		var feedback;
		if (data.message.validAnswer == data.message.myAnswer){
			feedback = "Good job!";
		}
		else {
			feedback = "Answer not correct; it was " + data.message.validAnswer;
		}
		$("#feedback").text(feedback);
	}
	else if (data.type == "sessionExpired") {
		var feedback = "Session aborted by teacher; correct answer was " +
										data.message.validAnswer;
		$("#feedback").text(feedback);
	}
};

onOpened = function(){};


