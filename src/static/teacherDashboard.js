var categories = new Array();
// global variables for the selection management
var clicking = false;
var allow_selection = false;
var min_Selected = 0;
var max_Selected = 0;
//----------------------------------------------


// function for the end selection management and the mouse tracking holes
$(document).mouseup(function(){
   		 clicking = false;
   		 min_Selected = 0;
   		 max_Selected = 0;
})

function fillTheHole(x,y){
	for (var i =x ; i< y; i++){
		$( "#char_id_"+i ).addClass("selected_teacher");
	}

}

function resetSelectionBinding_teacher(){
	$( "#dashboard" ).unbind( "mousedown" );
	$('#dashboard').mousedown(function(){
		$('.char_teacher').removeClass('selected_teacher');
	});
}


//---------------------------------------------


//worker thread for the graph
var w;

function startWorker() {
    if(typeof(Worker) !== "undefined") {
        if(typeof(w) == "undefined") {
            w = new Worker("/static/worker.js");
        }
        w.onmessage = function(event) {
	        if (event.data == "GetNewStats"){
		         $.post("/data/getSessionStatus"); 
	        }
        };
    } else {
        alert("Web Worker Not supported!");
    }
}

function stopWorker() { 
    w.terminate();
    w = undefined;
}

//--------------------------------------------




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
		var t1 = "Esercizio scelta categorie";
		var t2 = "Mostra le statistiche della lezione";
		var t3 = "Esercizio di selezione su:";
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
			.on("mousedown", startComplexExercise));
						
			
	$("#buttons").append($(document.createElement("div"))
			.attr("id", "showStats")
			.css("float","left")
			.css("display","inline")
			.css("margin-top","20px")
			.on("click", function(){$.get("/t/askStats");}));
			
			
			
	$("#showStats").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa-bar-chart" style="color:#000;font-size:40px;"></i><br/> '+t2+'</div></div></center>');		
		
		
	$("#newSimpleExercise").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa fa-pencil-square-o" style="color:#000;font-size:40px;"></i><br/> '+t1+'</div></div></center>');
	
	
	var selectHTMLString = '<select id="categorySelection" class="styled-select"><option>Nomi</option><option>Articoli</option><option>Aggettivi</option><option>Pronomi</option><option>Verbi</option><option>Avverbi</option><option>Preposizioni</option><option>Congiunzioni</option><option>Interiezioni</option></select>';
	
	$("#newComplexExercise").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa fa-pencil-square-o" style="color:#000;font-size:40px;"></i><br/> '+t3+'</div></div>'+selectHTMLString+'</center>');
	

			
		
	$('#categorySelection').mousedown(function(event){
		event.stopImmediatePropagation();	
	});

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
	console.log(message.data);
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
		if (data.message.focus == "on"){
			$('#'+data.message.studentName).css('color','#000');
			$('#'+data.message.studentName).html(data.message.studentName);
		}else if (data.message.focus == "off") {
			$('#'+data.message.studentName).css('color','red');
			$('#'+data.message.studentName).html(data.message.studentName + "(assente)");
		}	
	}
	else if (data.type == "studentFocusStatus") {
//	    console.log(data.message.studentName + " is going " + data.message.focus + " focus");
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
	else if (data.type == "exerciseExercise") {
		buildExercise(data.message);
	}
	else if (data.type == "exerciseStatus") {
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
        colors:[
        '#49A178',
        '#948C8A',
        '#FF4444'
        ],
        series: [{
            name: label,
            data: data

        }]
    });
}


function Comparator(a,b){
	if (a[0].word_index < b[0].word_index) return -1;
	if (a[0].word_index > b[0].word_index) return 1;
	return 0;
}

function updateChartData(answers, answersDict){
	var categoriesFromAnswer = new Array();
	var selectionEx = false;
	//controllo la lunghezza del dict, addesso è a 1 dovbrebbe essere 0 nel caso dell'esercizio complesso
	if (categories.length == 0 && answersDict.length ==1){
		selectionEx = true;
	}	
		
	if (selectionEx){	
		for (var answer in answers) {
			var answerJSON = JSON.parse(answer);
			var answerText = ""
			var selections  = answerJSON.answer.selections;
			//selections.sort(Comparator);
			for (var selection in answerJSON.answer.selections) {
				var textOfSelction = "";
				for (var fragment in answerJSON.answer.selections[selection]) {
					textOfSelction += answerJSON.answer.selections[selection][fragment].extent +" ";
				}
				answerText += textOfSelction.trim() + "/";
			}
			answerText = answerText.substring(0,answerText.length-1);
			//if (!$.inArray(answerText, categoriesFromAnswer)){
				categoriesFromAnswer.push(answerText);
			//}
		}
		
		initCharts(categoriesFromAnswer,'divise per categorie','Risposte');
		
	}
	var chart = $('#container').highcharts();
	var data = chart.series[0].data;
	
	
	
	
	for (var answer in answers) {
		
		var label = "";
		if (selectionEx){	
			var answerJSON = JSON.parse(answer);
			var answerText = ""
			var selections  = answerJSON.answer.selections;
			//selections.sort(Comparator);
				for (var selection in answerJSON.answer.selections) {
					var textOfSelction = "";
					for (var fragment in answerJSON.answer.selections[selection]) {
						textOfSelction += answerJSON.answer.selections[selection][fragment].extent +" ";
					}
					answerText += textOfSelction.trim() + "/";
				}
			
			answerText = answerText.substring(0,answerText.length-1);
			label = answerText;
		}
			
			
		
		
		
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
		
			
	
					
	var words = message.wordsList;
	var target = message.target;
	var answersProposed = message.answersProposed;
	
	
	if (target == -1 ){
		var label = $(document.createElement("div")).text("Seleziona tutti i "+message.category).addClass("instruction_teacher");
			$("#exercise").append(label);
		allow_selection=true;
	}
	
	var charid=1;
	
	for (var i = 0; i < words.length; i++) {
		var word = $(document.createElement("span"))
						.attr("id", words[i])
						.addClass("word_teacher");
		
		var parola = words[i]+"";
		
		for (var x = 0;x<parola.length;x++){
			var character = $(document.createElement("span"))
						.attr("id", "char_id_"+charid)
						.attr("char_number",charid)
						.attr("char_index_in_word",x)
						.attr("word",i)
						.addClass("char_teacher")
						.text(parola.substring(x,x+1));
			$(word).append(character);
			charid++;
		}
		
		
		$("#exercise").append(word);
		if (i == target) {
			$(word).css("color", "red");
		}	
	}
	
	
	
	
	$('.char_teacher').mousedown(function(event){
		event.stopImmediatePropagation();
    	clicking = true;
    	
    	
	});
	
	
	$('.char_teacher').mousemove(function(){
    if(clicking == false || allow_selection ==false) return;
    	
    	$( this ).addClass("selected_teacher");
    	
    	if ( min_Selected == 0 || parseInt($( this ).attr("char_number")) <= min_Selected){
    		min_Selected = parseInt($( this ).attr("char_number"));
    	}
    	
    	if ( max_Selected == 0 || parseInt($( this ).attr("char_number")) >= max_Selected){
    		max_Selected = parseInt($( this ).attr("char_number"));
    	}
    	fillTheHole(min_Selected,max_Selected);
    	
    	
    });
	
	if (target != -1 ){		
		$("#dashboard").append($(document.createElement("div"))
			.attr("id", "answers")
			.css("margin-top", "9px"));
		$("#answers").addClass("excercise");
		$("#answers").html("<br/>" + t2 + "<br/><br/>");
	}
	
	categories = new Array();
	for (var i = 0; i < answersProposed.length; i++ ){
		var answer = $(document.createElement("span"))
						.attr("id", answersProposed[i]["EN"])
						.text(answersProposed[i][language] + " ");
						
		
		categories.push(answersProposed[i][language]);
		$("#answers").append(answer);
	}
	
	if (target == -1 ){
		resetSelectionBinding_teacher();
	}
	
	
}

buildDashboard = function (status){
//	console.log(JSON.stringify(status));
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
		
		startWorker();
	};
};

onOpened = function(){};

startSimpleExercise = function () {
	$.get("/data/simple_exercise_request");
};
startComplexExercise = function () {
	var cat = $("#categorySelection").val();
	$.get("/data/complex_exercise_request?category="+cat);
};



askValidation = function () {
	//
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
			
			
			//stopWorker();
		//parte esercizio di selezione
		if (categories.length == 0 ){
			if ($('#selectionButtons').length <=0){
			var selectionButtons = $(document.createElement("div")).attr("id","selectionButtons").css('margin-top','15px').css('margin-bottom','15px').css('width','100%');
			var addButton = $(document.createElement("span")).attr("id","addButton").html('<i class="fa fa-plus-square-o"></i> ').css('font-size','40px').on("mousedown", function(event){event.stopImmediatePropagation(); addSelectionTotheList(addSelection());});

			$(selectionButtons).append(addButton);

			var selectionList = $(document.createElement("ul")).attr("id","selectionList");



			$("#exercise").append(selectionButtons);
			$("#exercise").append(selectionList);
			$("#exercise").append('<div id="sendButton"><center><div style="margin:0px;font-size:12px;" ><div class="send_button" onclick="sendExercise();">Controlla Esercizio<i class="fa fa fa fa-paper-plane" style="color:#000;font-size:30px;"></i></div></div></center></div>');
			}
			
		}
		
			
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
//			console.log(valid);
			$.post("/data/teacherValidation", {"valid": valid});
			$("#answers").children().off("click");
			newExercise();
		});
	}
};



function addSelection(){

	if (allow_selection){

		var testo = "";

		var wordID = -1;
		var charID = -1;

		var fragment = {};
		var selection = new Array();

		var seletedCharInWord = 0;
		var selectionHead = 0;
		
		var numItems = $('.selected_teacher').length
		if (numItems == 0){
			return selection;
		}
		
		
		
		$(".selected_teacher").each(function() {
				var currentWordId = parseInt($(this).attr('word'));
				var currentCharIndex = parseInt($(this).attr('char_index_in_word'));

				if (wordID == -1){
					selectionHead = currentCharIndex;
				}

				seletedCharInWord++;

				if (currentWordId != wordID){


					fragment.start = selectionHead;
					fragment.end  = selectionHead+(seletedCharInWord);

					if (wordID != -1){
						fragment.word_index = wordID;
						fragment.extent = testo.trim();
						selection.push(fragment);
						fragment = {};

					}
					wordID = currentWordId;
					seletedCharInWord = 0;
					selectionHead = currentCharIndex;
					testo ="";
				}

				testo +=($(this).text())+"";
				$(this).removeClass('selected_teacher');
		});


		fragment = {};
		fragment.start = selectionHead;
		fragment.end = selectionHead + (seletedCharInWord+1);
		fragment.extent = testo.trim();
		fragment.word_index = wordID ;
		selection.push(fragment);


		return selection;
	}
	//console.log(JSON.stringify(answerJSON));

}

function addSelectionTotheList(selection){
	if (allow_selection){
		if (selection.length > 0){
			var testo= "";
	
			for (var idx in selection) {
				var frag = selection[parseInt(idx)];
				testo += frag.extent +" ";
	
			}
			var listItem = $(document.createElement("li")).html('<span style="cursor:pointer;" onclick="selectionClicked($(this).parent())">'+testo.trim()+'</span> <i class="fa fa-minus-square-o" style="cursor:pointer;" onclick="removeSelectionFromtheList($(this).parent())"></i>').addClass("selectionListItem");
	
			$('#selectionList').append(listItem);
			$(listItem).data("selection_teacher",selection);
		}
	}
}


function removeSelectionFromtheList(obj){
	if (allow_selection){
		$(obj).remove();
	}
}

function selectionClicked(obj){
	resetSelectionBinding_teacher();
	var data  = $(obj).data("selection_teacher");
	for (var idx in data) {
		var frag = data[parseInt(idx)];


		for (var x = frag.start ; x < frag.end ;x++){
			$(".char_teacher[char_index_in_word='"+x+"'][word='"+frag.word_index+"']").addClass("selected_teacher");
		}
	}


}

function sendExercise(){
	
	var answerJSON = {};
	var answer ={};

	var selections = new Array();


	var language = getLanguage();
	
	if (language == "EN") {
		var t2 = "Show Lesson Statistics";
	}
	else if (language == "IT") {
		var t2 = "Mostra le statistiche della lezione";
	}
	
	
	
	$(".selectionListItem").each(function() {
		selections.push($(this).data("selection_teacher"));
	});
	allow_selection=false;
	$("#sendButton").remove();
	
	
	answer.selections =selections;
	answerJSON.answer  = answer;
//	console.log(JSON.stringify(answerJSON))
	$.ajax({
		url: "/data/teacherValidation",
		type: "POST",
		data: { valid : JSON.stringify(answerJSON)},
		datatype : "html",
		contentType: "application/x-www-form-urlencoded; charset=UTF-8"	,
    	traditional: true

	});
	
	
	$("#buttons").append($(document.createElement("div"))
			.attr("id", "showStats")
			.css("float","left")
			.css("display","inline")
			.css("margin-top","20px")
			.on("click", function(){$.get("/t/askStats");}));
			
			
			
	$("#showStats").html('<center><div style="margin:0px;font-size:12px;cursor:pointer;"><div class="start_button"><i class="fa fa-bar-chart" style="color:#000;font-size:40px;"></i><br/> '+t2+'</div></div></center>');
	
	
	
}


