// globals



var categories = new Array();




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
	
	/*
	var btn = document.createElement('button');
	btn.setAttribute('id', 'startExercise');
	btn.innerHTML = t1;
	
	
	var btn2 = document.createElement('button');
	btn2.setAttribute('id', 'startExercise');
	btn2.innerHTML = t1;
	
	$("#dashboard").append(btn);
	$("#dashboard").append(btn2);
	*/
	
	
	if ($("#newExercise").length > 0){
		 	 $('#newExercise').remove();
	}
	
	
	
	$("#dashboard").before($(document.createElement("button"))
			.attr("id", "newExercise")
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
	
	$("#progress_text").remove();
	$('#progressbar').remove();
	
	
	
	if ($("#container").length > 0){
		 	 $('#container').highcharts().destroy();
		 	 $('#container').remove();
	}
	
	$("#dashboard").append($(document.createElement("div"))
				.attr("id", "container")
				.css("min-width","310px")
				.css("height","300px")
				.css("margin","0 auto")
				.css("width","80%")
				.text(t1 + ": "));
				
	
	
	var studentsArray = new Array();
	
	var stats = message.stats;
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "stats")
			.css("display", "none")
			.text(t1));
	for (name in stats) {
		studentsArray.push(name);
		$("#stats").append($(document.createElement("div"))
				.text(name + ": " + stats[name] + " correct answers"));
	}
	
	initCharts(studentsArray,'divise per studenti','Risposte Corrette');
	updateChartDataStudents(stats);
	
	
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



function initCharts(cat,subtitle,label){


var data = new Array();

for (var name in cat) {
	data.push(0);
}


$('#container').highcharts({
        chart: {
        	type: 'column'
        },
        title: {
            text: 'Risposte della Classe'
        },
        subtitle: {
            text: subtitle
        },
        xAxis: {
            categories: cat
        },
        yAxis: {
        	allowDecimals: false,
            min: 0,
            title: {
                text: 'risultati'
            }
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [{
            name: label,
            data: data

        }]
    });
}


function updateChartData(answers){
	var chart = $('#container').highcharts();
	var data = chart.series[0].data;
	for (var answer in answers) {
	
	
		/* c'è ma  non ci dovrebbe essere */
		var label = "";
		if (answer.toLowerCase() == "noun"){
				label = "Nome";
		} else if (answer.toLowerCase() == "adjective"){
				label = "Aggettivo";
		}else if (answer.toLowerCase() == "verb"){
				label = "Verbo";
		}else if (answer.toLowerCase() == "adverb"){
				label = "Avverbio";
		}else if (answer.toLowerCase() == "other"){
				label = "Altro";
		}else {
			label = answer.toLowerCase()
		}
		/*    */
		
		
		
		
		for (var i = 0; i < data.length; i++ ){
			if (data[i].category == label){
				data[i].y = answers[answer].length;
				
				var students = "";
				for (var x = 0; x < answers[answer].length; x++){
					students = students + answers[answer][x] +", "
				
				}	
				data[i].name = students;
			}
		
		}
		
	};

    chart.series[0].setData(data);
   
}

function updateChartDataStudents(students){
	var chart = $('#container').highcharts();
	var data = chart.series[0].data;
	
	for (name in students) {
		
		for (var i = 0; i < data.length; i++ ){
			if (data[i].category == name){
				data[i].y = students[name]
			}
		}
	}
	
    chart.series[0].setData(data);
   
}







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
			.css("font-weight", "bold"));
	$("#exercise").addClass("excercise");
	$("#exercise").html(t1 + "<br/>");
			
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "answers")
			.css("margin-top", "9px"));
	$("#answers").addClass("excercise");
	$("#answers").html("<br/>" + t2 + "<br/>");
			
			
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
			$(word).css("color", "red");
		}
	}
	categories = new Array();
	for (var i = 0; i < answersProposed.length; i++ ){
		var answer = $(document.createElement("span"))
						.attr("id", answersProposed[i]["EN"])
						.text(answersProposed[i][language] + " ");
						
		
		categories.push(answersProposed[i][language]);
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
		var t5 = "Answered";
	}
	else if (language == "IT"){
		var t1 = "RISPOSTE DEGLI STUDENTI";
		var t2 = "BARRA DI STATO";
		var t3 = "Mancanti";
		var t4 = "Tutti gli studenti hanno risposto";
		var t5 = "Risposte";
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
				.css("display","none")
				.text(t1 + ": "));
		for (var answer in answers) {
			
			var a = $(document.createElement("div"));
			$(a).append($(document.createElement("div"))
					.addClass("title")
					.css("display","none")
					.text(answer.toUpperCase()));
			$("#studentAnswers").append(a);
			for (var i = 0; i < answers[answer].length; i++){
				var b = $(document.createElement("div"))
						.css("display","none")
						.text(answers[answer][i]);
				a.append(b);
			};	
		};
		updateChartData(answers);
	}
	
	
	
	
	
	function statusBar(status){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "statusBar")
				.css("margin-top","35px")
				.css("display","none")
				.text(t2 + ": "));
				
				
		var total = status.missing.length + status.answered.length;
		 $("#progress_text").remove();
		 $('#progressbar').remove();
		 
		$("#dashboard").append('<div style="margin-top:35px;"><div id="progressbar" class="progress progress-striped active" style="position:absolute;display:inline;width: 400px;"><div class="bar" style="width: ' + (status.answered.length / total)*100 + '%;"></div></div><span id="progress_text" style="margin-left:420px;position:absolute;display:inline;font-size:14px; margin-top: 0px;"></span></div>');
		
		var txt;
		txt = " "+t5+": "+status.answered.length+" --> "+status.answered;
		
		$("#progress_text").append(txt);

		if (status.missing.length > 0){
			txt = " " + t3 + ": "+status.missing.length+" --> "+status.missing;
			color = null;
		}
		else {
			txt = " " + t4;
			color = "Green";
			$("#progressbar").removeClass("active");
			$("#progressbar").removeClass("progress-striped");
			
		}
		$("#progress_text").append(txt);
		
		if ($("#container").length > 0){
		 	 $('#container').highcharts().destroy();
		 	 $('#container').remove();
		}
	
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "container")
				.css("min-width","310px")
				.css("height","300px")
				.css("margin-top","75px")
				.css("width","400px")
				.css("right","30px")
				.text(t2 + ": "));
				
		initCharts(categories,'divise per categorie','Risposte');

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
		$("#answers").children().css("color", "blue");
		var instr = $(document.createElement("span"))
			.attr("id", "askValidation")
			.css("color", "Green")
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
					$(studentAnswers[i]).css("color", "Green");					
				}
			}
			$.post("/data/teacherValidation", {"valid": valid});
			$("#answers").children().off("click");
			newExercise();
		});
	}
};
