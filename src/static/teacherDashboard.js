var categories = new Array();
$(document).ready(function () {
	newExercise();
	$(".studentName").on("click", function(event){
	    attachStatRequest(event.target.id);
	});
	$("body").css("background","url(../static/images/paper_texture.jpg)" );
});
onError = function (){
	askMeRefresh();
	$.get("/channelExpired");
};
onClose = function (){};
newExercise = function (){
	var language = getLanguage(); 
	if (language == "EN") {
		var t1 = "Start Simple Exercise";
		var t2 = "Show Lesson Statistics";
		var t3 = "Start Complex Exercise";
	}
	else if (language == "IT") {
		var t1 = "Inizia un nuovo esercizio semplice";
		var t2 = "Mostra le statistiche della lezione";
		var t3 = "Inizia un nuovo esercizio complesso";
	}
	if ($("#newSimpleExercise").length > 0){
		 	 $("#newSimpleExercise").remove();
		 	 $("#newComplexExercise").remove();
		 	 $("#showStats").remove();
		 	 $('#buttons').empty();
		 	 
	}
	$("#buttons").append($(document.createElement("div"))
			.attr("id", "newSimpleExercise")
			.css("float","left")
			.css("display","inline")
			.css("margin-top","20px")
			.on("click", startSimpleExercise));
	$("#buttons").append($(document.createElement("div"))
			.attr("id", "newComplexExercise")
			.css("float","left")
			.css("display","inline")
			.css("margin-top","20px")
			.on("click", startComplexExercise));
						
			
	$("#buttons").append($(document.createElement("div"))
			.attr("id", "showStats")
			.css("float","left")
			.css("display","inline")
			.css("margin-top","20px")
			.on("click", function(){$.get("/t/askStats");}));
			
	$("#newSimpleExercise").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa fa-pencil-square-o" style="color:#000;font-size:40px;"></i><br/> '+t1+'</div></div></center>');
	$("#newComplexExercise").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa fa-pencil-square-o" style="color:#000;font-size:40px;"></i><br/> '+t3+'</div></div></center>');

	$("#showStats").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa-bar-chart" style="color:#000;font-size:40px;"></i><br/> '+t2+'</div></div></center>');		
			
			
			

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
	$(document.getElementById(student))
	    .append(s)
	    .off("click").on("click", function(){
		$(this).children().remove();
		$(this).css("background-color", "transparent");
		$(this).off("click").on("click", function(event){
		    attachStatRequest(event.target.id);
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
		 $('#progress_container').remove();
	
	
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
				.css("overflow","hidden")
				.text(t1 + ": "));
				
	
	
	var studentsArray = new Array();
	
	var stats = message.stats;
        // qui il nuovo dizionario con le statistiche dettagliate
        //
        var fullstats = message.fullstats;
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
	updateChartDataStudents(fullstats);
	
	
};

function attachStatRequest(id){
    var student = id;
    $.post("/t/askStudentStats", {"student": student});
}

onMessage = function(message) {
	var language = getLanguage();
	var data = JSON.parse(message.data);
	if (data.type == "studentArrived") {
		var studentName = data.message.studentName;
		var studentFullName = data.message.studentFullName;
		var studentsCount = $(".studentName").length;
		var txt = studentFullName;
		var student = $(document.createElement("li"))
		    .attr("id", studentName)
		    .addClass("studentName")
		    .text(studentFullName)
		    .on("click", function(event){
			attachStatRequest(event.target.id);
		    });
		$("#students").append(student);
	}
	else if (data.type == "studentLogout") {
		$("#" + data.message.studentName).remove();
	}
	else if (data.type == "studentFocusStatus") {
	    console.log(data.message.studentName + " is going " + data.message.focus + " focus");
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
		if ($("#" + data.message.studentName).children(".pingRequest").length == 0){
			$("#" + data.message.studentName).append($(document.createElement("button"))
					.addClass("pingRequest")
					.text(t1)
					.on("click", function(event){
						var student = event.target.parentElement.id;
						$.post("/ping", {"student": student});
					}));
			$("#" + data.message.studentName).append($(document.createElement("button"))
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
		if ($("#" + data.message.studentName).children(".pingRequest").length > 0){
			$("#" + data.message.studentName).children(".pingRequest").remove();
			$("#" + data.message.studentName).children(".logoutStudent").remove();
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
        	backgroundColor: 'transparent',
        	type: 'column',
        	animation: false
        },
        title: {
            text: 'Risposte della Classe'
        },
        subtitle: {
            text: subtitle
        },
        xAxis: {
            categories: cat,
            lineColor: '#000',
             gridLineColor: '#000'
        },
        yAxis: {
        	allowDecimals: false,
            lineColor: '#000',
            gridLineColor: '#000',
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

function updateChartData(answers, answersDict){
	var chart = $('#container').highcharts();
	var data = chart.series[0].data;
	for (var answer in answers) {
		var label = "";
		for (var i = 0; i < answersDict.length; i++){
			if (answersDict[i]["EN"] == answer){
				label = answersDict[i]["IT"];
			}
		}
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
	
	var emptySeries = new Array();
	for (var i = 0; i < students.length; i++ ){
		emptySeries.push(0);
	}
	
	var data = chart.series[0].data;
	
	chart.addSeries({name: "Mancanti", data: emptySeries});
	chart.addSeries({name: "Sbagliate", data: emptySeries});
	

	
	chart.series[1].setData(emptySeries);
    chart.series[2].setData(emptySeries);
    
    var correct = chart.series[0].data;
    var missed = chart.series[1].data;
	var wrong = chart.series[2].data;
	
	for (var idx_student = 0;idx_student < students.length ; idx_student++) {
		
		for (var i = 0; i < data.length; i++ ){
			if (data[i].category == students[idx_student].studentName){
				correct[i].y = students[idx_student].stats.correct;
				missed[i].y = students[idx_student].stats.missing;
				wrong[i].y = students[idx_student].stats.wrong;
			}
		}
	}
	
    chart.series[0].setData(correct);
    chart.series[1].setData(missed);
    chart.series[2].setData(wrong);
   
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
	
	
	
	$("#buttons").append($(document.createElement("div"))
			.attr("id", "timeIsUp")
			.css("float","left")
			.css("display","inline")
			.css("margin-top","20px")
			.on("click", askValidation));
	

				
	$("#timeIsUp").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa-clock-o" style="color:#000;font-size:40px;"></i><br/> '+t3+'</div></div></center>');		
				
		
	
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "exercise")
			.css("font-weight", "bold")
			.css("clear","both")
	);
			
	$("#exercise").addClass("excercise");
	$("#exercise").html(t1 + "<br/>");
			
	$("#dashboard").append($(document.createElement("div"))
			.attr("id", "answers")
			.css("margin-top", "9px"));
	$("#answers").addClass("excercise");
	$("#answers").html("<br/>" + t2 + "<br/><br/>");
					
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
	answersGraph(status.message.possibleAnswers, status.message.dictAnswers);

	
	
	function cleanDashboard () {
		$("#studentAnswers, #statusBar").remove();
	};
	
	function answersGraph(answers, dictAnswers){
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
		updateChartData(answers, dictAnswers);
	}
	
	function statusBar(status){
		$("#dashboard").append($(document.createElement("div"))
				.attr("id", "statusBar")
				.css("margin-top","0")
				.css("display","none")
				.text(t2 + ": "));
				
				
		var total = status.missing.length + status.answered.length;
		 $("#progress_text").remove();
		 $('#progressbar').remove();
		 $('#progress_container').remove();
		 
		$("#dashboard").append('<div id="progress_container" style="margin-top:35px;"><div id="progressbar" class="progress progress-striped active" style="margin:0 auto;width: 400px;"><div class="bar" style="width: ' + (status.answered.length / total)*100 + '%;"></div></div><br/><center><div id="progress_text" style="margin:0 auto;font-size:14px;"></div></center></div>');
		
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
			
			askValidation();
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
				.css("width","70%")
				.css("right","30px")
				.css("overflow","hidden")
				.css("margin","0 auto")
				.text(t2 + ": "));
				
		initCharts(categories,'divise per categorie','Risposte');

	};
};

onOpened = function(){};

startSimpleExercise = function () {
	$.get("/data/simple_exercise_request");
};
startComplexExercise = function () {
	$.get("/data/complex_exercise_request");
};

askValidation = function () {
	var language = getLanguage();
	if (language == "EN")
		var t1 = "Click on the right answer";
	else if (language == "IT")
		var t1 = "Clicca sulla risposta giusta";
	if ($("#askValidation").length == 0) {
		$("#timeIsUp").remove();
		$.get("/t/timeIsUp");
		$("#answers").children().css("cursor", "pointer");
		$("#answers").children().addClass("answer_teacher_button");
		
		
		
		
		var instr = $(document.createElement("div"))
			.attr("id", "askValidation")
			.css("color", "Green")
			.text(t1);
		$("#answers").append(instr);
		$("#answers").children().on("click", function (event){
			var valid = event.target.id;
			$("#askValidation").remove();
			$(event.target).css("background-color", "Green");
			$(event.target).css("color", "#fff");
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
