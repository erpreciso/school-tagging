$(document).ready(function () {
	initializeDashboard();
});

onError = function (){
	askMeRefresh();
	$.get("/channelExpired");
};
onClose = function (){};

onMessage = function(message) {
	console.log(message);
	var data = JSON.parse(message.data);
	console.log(data);
	var language = getLanguage(); 
	if (language == "EN")
		var t1 = "Session aborted by teacher; correct answer was ";
	else if (language == "IT")
		var t1 = "Esercizio interrotto dall'insegnante; la risposta esatta era ";
	if (data.type == "sessionExercise")
		presentExercise(data.message);
	else if (data.type == "validAnswer")
		feedbackFromTeacher(data.message);
	else if (data.type == "lessonTerminated")
		lessonTerminated();
	else if (data.type == "pingFromTeacher")
		$.post("/ping", {"alive": true});
	else if (data.type == "sessionExpired") {
		var feedback = t1 + data.message.validAnswer;
		$("#feedback").text(feedback)
				.css("color", "LightGoldenRodYellow ");
	}
};

function lessonTerminated () {
	var language = getLanguage(); 
	if (language == "EN")
		var t1 = "Lesson terminated by teacher";
	else if (language == "IT")
		var t1 = "Lezione interrotta dall'insegnante";
	$("#lessonName").text(t1);
	$("#exercise, #answers").remove();
	if ($("#feedback").length > 0){
		$("#feedback").remove();
	}
}

function mixArray(arr) {
	var mixed = [];
	var howmany = arr.length * 1;
	for (var i = 0; i < howmany; i++){
		var pos = Math.floor(Math.random() * arr.length);
		mixed[i] = arr.splice(pos, 1);
	}
	return mixed;
}

function presentExercise(message) {
	var language = getLanguage(); 
	$("#exercise, #answers").empty();
	if ($("#feedback").length > 0){
		$("#feedback").remove();
	}
	$("#answers").css("padding-top", "20px")
	var words = message.wordsList;
	var target = message.target;
	console.log("raw from py");
	console.log(message.answersProposed);
	var answersProposed = mixArray(message.answersProposed);
	console.log("mixed");
	console.log(answersProposed);
	for (var i = 0; i < words.length; i++) {
		var word = $(document.createElement("span"))
						.attr("id", words[i])
						.text(words[i] + " ");
		$("#exercise").append(word);
		if (i == target) {
			$(word).css("color", "yellow");
		}
	}
	for (var i = 0; i < answersProposed.length; i++ ){
		console.log(answersProposed[i][0]["EN"]);
		var answer = $(document.createElement("span"))
			.attr("id", answersProposed[i][0]["EN"])
			.css("color", "Moccasin")
			.css("margin-right", "10px")
			.text(answersProposed[i][0][language] + " ");
		
		$("#answers").append(answer);
		var par = {"answer": answersProposed[i][0]["EN"]};
		$(answer).on("click", par ,function(event){
			var triggered = event.target.id;
			$("#" + triggered).css("color", "#a6e22e");
			$("#" + triggered).css("text-decoration", "underline");
			$.post("/data/answer", {"answer": triggered});
			$("#answers").children().off("click");
			
			
			if (language == "EN")
				var t1 = "Waiting for teacher to assess...";
			else if (language == "IT")
				var t1 = "Attendi la validazione dell'insegnante";
			
			$("#feedback").text(t1);
			
			
		});
	}
	var feedback = $(document.createElement("div"))
				.attr("id", "feedback")
				.css("margin-top", "15px");
		
	$("#answers").after(feedback);
}

function feedbackFromTeacher(message) {
	var feedback;
	var background;
	var language = getLanguage(); 
	if (language == "EN") {
		var t1 = "Good job!";
		var t2 = "Answer not correct; it was "; 
	}
	else if (language == "IT") {
		var t1 = "Risposta esatta!";
		var t2 = "Risposta non corretta; quella giusta era ";
	}
	if (message.validAnswer == message.myAnswer){
		feedback = t1;
		background = "GreenYellow";
	}
	else {
		var italianAnswer = "";
		for (var i = 0; i < message.dict.length; i++){
			if (message.dict[i]["EN"] == message.validAnswer){
				italianAnswer = message.dict[i]["IT"];
			}
		}
		feedback = t2 + italianAnswer;
		background = "Red";
	}
	$("#feedback").text(feedback).css("color", background);
}

onOpened = function(){};

function initializeDashboard(){
	var language = getLanguage(); 
	if (language == "EN")
		var t1 = "Waiting for exercise to start...";
	else if (language == "IT"){
		var t1 = "Attendi l'inizio dell'esercizio";
	}
	$("#lessonName").after($(document.createElement("div"))
			.attr("id", "exercise")
			.text(t1));
	$("#exercise").after($(document.createElement("div"))
			.attr("id", "answers"));
};
