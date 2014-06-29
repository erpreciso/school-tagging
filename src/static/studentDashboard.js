$(document).ready(function () {
	//~ $("#startExercise").on("click", startExercise);
	
});

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "session") {
		$("#exercise").children().remove();
		var words = data.message.wordsList;
		//~ console.log(data.message);
		for (var i = 0; i < words.length; i++) {
			var word = $(document.createElement("span"))
							.attr("id", words[i])
							.addClass("answer")
							.text(words[i] + " ");
			$("#exercise").append(word);
			$(word).on("click", function (){
				alert(words[i]);
			});
		}
	}
}

onOpened = function(){};


