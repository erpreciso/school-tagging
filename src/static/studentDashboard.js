$(document).ready(function () {
	//~ $("#startExercise").on("click", startExercise);
	
});

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "session") {
//		$("#exercise").children().remove();
		$("#exercise, #answers").empty();
		var words = data.message.wordsList;
		var target = data.message.target;
		var answersProposed = data.message.answersProposed;
		//~ console.log(data.message);
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
				$("#answers").after("Waiting for teacher to assess...");
			});
		}
	}
};

onOpened = function(){};


