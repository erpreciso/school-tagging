$(document).ready(function () {
    initializeDashboard();
});

var answerJSON = {};
var selections = new Array();

$(document).bind('touchend mouseup',function(){
   		 clicking = false;
   		 min_Selected = 0;
   		 max_Selected = 0;
   		
})

var selectionExercise = false;

var clicking = false;
var allow_selection = false;
var min_Selected = 0;
var max_Selected = 0;

window.onblur = imnotfocused;
window.onfocus = imfocused;

function imnotfocused(){
    $.post("/focus",{"focus": "off"});
}

function imfocused(){
    $.post("/focus",{"focus": "on"});
}

onError = function (){
	askMeRefresh();
	$.get("/channelExpired");
};
onClose = function (){};

onMessage = function(message) {
//        console.log(message)
	var data = JSON.parse(message.data);
	var language = getLanguage();
	if (language == "EN")
		var t1 = "Session aborted by teacher; correct answer was ";
	else if (language == "IT")
		var t1 = "Esercizio interrotto dall'insegnante; la risposta esatta era ";
	if (data.type == "exerciseExercise"){
		localStorage.setItem("exerciseID", data.message.id);
        presentExercise(data.message);}
	else if (data.type == "validAnswer")
		feedbackFromTeacher(data.message);
	else if (data.type == "lessonTerminated")
		lessonTerminated();
	else if (data.type == "pingFromTeacher")
		$.post("/ping", {"alive": true});
	else if (data.type == "exerciseExpired") {
		
		var validAnswerTextFromJSON ="";
		
		if (selectionExercise){
			var answerJSON = JSON.parse(data.message.validAnswer);
			var selections  = answerJSON.answer.selections;
			for (var selection in answerJSON.answer.selections) {
				var textOfSelction = "";
				for (var fragment in answerJSON.answer.selections[selection]) {
					textOfSelction += answerJSON.answer.selections[selection][fragment].extent +" ";
				}
				validAnswerTextFromJSON += textOfSelction.trim() + "/";
			}
			validAnswerTextFromJSON = validAnswerTextFromJSON.substring(0,validAnswerTextFromJSON.length-1);
		}
		
		
		
		var italianAnswer = "";
//                console.log(data.message);
		for (var i = 0; i < data.message.dict.length; i++){
			if (data.message.dict[i]["EN"] == data.message.validAnswer){
				italianAnswer = data.message.dict[i]["IT"];
			}
		}
                var feedback = t1 + italianAnswer + validAnswerTextFromJSON;
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

function fillTheHole(x,y){
	for (var i =x ; i< y; i++){
		$( "#char_id_"+i ).addClass("selected");
	}

}




function presentExercise(message) {
	answerJSON = {};
	selections = new Array();
	var language = getLanguage();
	$("#exercise, #answers").empty();
	if ($("#feedback").length > 0){
		$("#feedback").remove();
	}

	$("#answers").css("padding-top", "20px")
	var words = message.wordsList;
	var target = message.target;


	if (target == -1 ){
		var label = $(document.createElement("div")).text("Seleziona tutti i "+message.category).addClass("instruction");
			$("#exercise").append(label);
		allow_selection=true;
		selectionExercise = true;
	}else{
			selectionExercise = false;
	}


	//console.log("raw from py");
	//console.log(message.answersProposed);
	var answersProposed = mixArray(message.answersProposed);
	//console.log("mixed");
	//console.log(answersProposed);
	var charid=1;

	for (var i = 0; i < words.length; i++) {
		var word = $(document.createElement("span"))
						.attr("id", words[i])
						.addClass("word");

		var parola = words[i]+"";

		for (var x = 0;x<parola.length;x++){
			var character = $(document.createElement("span"))
						.attr("id", "char_id_"+charid)
						.attr("char_number",charid)
						.attr("char_index_in_word",x)
						.attr("word",i)
						.addClass("char")
						.text(parola.substring(x,x+1));
			$(word).append(character);
			charid++;
		}


		$("#exercise").append(word);
		if (i == target) {
			$(word).css("color", "yellow");
		}



	}

	$('.char').bind('touchstart mousedown',function(event){
		event.preventDefault();
		event.stopImmediatePropagation();
    	clicking = true;
	});



	/*
	$('.char').mousedown(function(event){
		event.stopImmediatePropagation();
    	clicking = true;
	});
*/

	$('.char').bind('touchmove mousemove',function(event){
		event.preventDefault();
		if (event.type.toLowerCase() == "touchmove")
			clicking=true;
		if(clicking == false || allow_selection ==false) return;




		var element = this;
		if (event.type.toLowerCase() == "touchmove"){
			
			var x = event.originalEvent.touches[0].clientX;
			var y = event.originalEvent.touches[0].clientY;
			//alert(x+" - "+y);
			element = document.elementFromPoint(x,y);
			if($(element).hasClass("char") ==false) return;
			//alert(element);
			
		}

    	$( element ).addClass("selected");

    	if ( min_Selected == 0 || parseInt($( element ).attr("char_number")) <= min_Selected){
    		min_Selected = parseInt($( element ).attr("char_number"));
    	}

    	if ( max_Selected == 0 || parseInt($( element ).attr("char_number")) >= max_Selected){
    		max_Selected = parseInt($( element ).attr("char_number"));
    	}
    	fillTheHole(min_Selected,max_Selected);
		

    });



	if (target == -1 ){
		selectionExercise = true;
		var selectionButtons = $(document.createElement("div")).attr("id","selectionButtons").css('margin-top','15px').css('margin-bottom','15px');
		var addButton = $(document.createElement("span")).attr("id","addButton").html('<i class="fa fa-plus-square-o"></i> ').css('font-size','40px').on("mousedown", function(event){event.stopImmediatePropagation(); addSelectionTotheList(addSelection());});

		$(selectionButtons).append(addButton);

		var selectionList = $(document.createElement("ul")).attr("id","selectionList");



		$("#exercise").append(selectionButtons);
		$("#exercise").append(selectionList);
		$("#exercise").append('<div id="sendButton"><center><div style="margin:0px;font-size:12px;" ><div class="send_button" onclick="sendExercise();">Finito!<br/>Invia all\'insegnante <i class="fa fa fa fa-paper-plane" style="color:#fff;font-size:30px;"></i></div></div></center></div>');
	}else{
		selectionExercise = false;
	}



	for (var i = 0; i < answersProposed.length; i++ ){
		//console.log(answersProposed[i][0]["EN"]);
		var answer = $(document.createElement("span"))
			.attr("id", answersProposed[i][0]["EN"])
			.css("color", "Moccasin")
			.css("margin-right", "10px")
			.css("cursor", "pointer")
			.addClass("answer_button")
			.text(answersProposed[i][0][language] + " ");

		$("#answers").append(answer);
		var par = {"answer": answersProposed[i][0]["EN"]};
		$(answer).on("click", par ,function(event){
			var triggered = event.target.id;
			$("#" + triggered).css("color", "#fff");
			$("#" + triggered).css("text-decoration", "underline");
			$("#" + triggered).css("background-color", "orange");
			$("#" + triggered).addClass("answered");

			$.post("/data/answer", {
                  "answer": triggered,
                  "exerciseID": localStorage.getItem("exerciseID")
                  });
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


	resetSelectionBinding();




}

function addSelection(){

	if (allow_selection){

		var testo = "";

		var wordID = -1;
		var charID = -1;

		var fragment = {};
		var selection = new Array();

		var seletedCharInWord = 0;
		var selectionHead = 0;
		
		var numItems = $('.selected').length
		if (numItems == 0){
			return selection;
		}
		
		
		
		$(".selected").each(function() {
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
				$(this).removeClass('selected');
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
				$(listItem).data("selection",selection);
		}
	}
}


function removeSelectionFromtheList(obj){
	if (allow_selection){
		$(obj).remove();
	}
}

function selectionClicked(obj){
	resetSelectionBinding();
	var data  = $(obj).data("selection");
	for (var idx in data) {
		var frag = data[parseInt(idx)];


		for (var x = frag.start ; x < frag.end ;x++){
			$(".char[char_index_in_word='"+x+"'][word='"+frag.word_index+"']").addClass("selected");
		}
	}


}




function resetSelectionBinding(){
	$( ".student_block" ).unbind( "mousedown" );
	$('.student_block').mousedown(function(){
		$('.char').removeClass('selected');
	});
}


function sendExercise(){
	
	
	/*var numItems = $('.selectionListItem').length
		if (numItems == 0){
			alert("Seleziona almeno una porzione di testo");
			return ;
		}
	*/
	
	var answerJSON = {};
	var answer ={};

	var selections = new Array();


	var language = getLanguage();
	$(".selectionListItem").each(function() {
		selections.push($(this).data("selection"));
	});
	allow_selection=false;
	$("#sendButton").remove();
	if (language == "EN")
				var t1 = "Waiting for teacher to assess...";
			else if (language == "IT")
				var t1 = "Attendi la validazione dell'insegnante";

	$("#feedback").text(t1);
	answer.selections =selections;
	answerJSON.answer  = answer;
	console.log(JSON.stringify(answerJSON));
	$.ajax({
		url: "/data/answer",
		type: "POST",
		data: { answer : JSON.stringify(answerJSON),
                  "exerciseID": localStorage.getItem("exerciseID")},
		datatype : "html",
		contentType: "application/x-www-form-urlencoded; charset=UTF-8"	,
    	traditional: true

	});
	//$.post("/data/answer", { "answer" : JSON.stringify(answer)} );

}

function arraysEqual(arr1, arr2) {
    if(arr1.length !== arr2.length)
        return false;
    for(var i = arr1.length; i--;) {
        if(arr1[i] !== arr2[i])
            return false;
    }

    return true;
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
	
	var validAnswerTextFromJSON = "";
	var jsonEquivalence = false;
	
	if (selectionExercise){	
		
		if (message.validAnswer.length != message.myAnswer.length){
			jsonEquivalence = false;
			var answerJSON = JSON.parse(message.validAnswer);
			var selections  = answerJSON.answer.selections;
			for (var selection in answerJSON.answer.selections) {
				var textOfSelction = "";
				for (var fragment in answerJSON.answer.selections[selection]) {
					textOfSelction += answerJSON.answer.selections[selection][fragment].extent +" ";
				}
				validAnswerTextFromJSON += textOfSelction.trim() + "/";
			}
			validAnswerTextFromJSON = validAnswerTextFromJSON.substring(0,validAnswerTextFromJSON.length-1);
		}else{
			
			var validArray = new Array();
			var answerArray = new Array();
			
			var validJSON = JSON.parse(message.validAnswer);
			
			for (var selection in validJSON.answer.selections) {
				
				var selectionLenght = 0;
				for (var fragment in validJSON.answer.selections[selection]) {
					validArray.push(validJSON.answer.selections[selection][fragment].extent);
					validArray.push(validJSON.answer.selections[selection][fragment].start);
					validArray.push(validJSON.answer.selections[selection][fragment].end);
					validArray.push(validJSON.answer.selections[selection][fragment].word_index);
					selectionLenght += validJSON.answer.selections[selection][fragment].extent.length;
				}
				validArray.push(selectionLenght);
			}
			
			var answerJSON = JSON.parse(message.myAnswer);
			
			for (var selection in answerJSON.answer.selections) {
				var selectionLenght = 0;
				for (var fragment in answerJSON.answer.selections[selection]) {
					answerArray.push(answerJSON.answer.selections[selection][fragment].extent);
					answerArray.push(answerJSON.answer.selections[selection][fragment].start);
					answerArray.push(answerJSON.answer.selections[selection][fragment].end);
					answerArray.push(answerJSON.answer.selections[selection][fragment].word_index);
					selectionLenght += answerJSON.answer.selections[selection][fragment].extent.length;
				}
				validArray.push(selectionLenght);
			}
			validArray.sort();
			answerArray.sort();
			
			
			jsonEquivalence = arraysEqual(validArray, answerArray);
			
			
			
			
			
			
		}
		
		
		
	}
	
	
	
	
	
	
	if (message.validAnswer == message.myAnswer || jsonEquivalence){
		feedback = t1;
		background = "Green";
	}
	else {
		var italianAnswer = "";
		for (var i = 0; i < message.dict.length; i++){
			if (message.dict[i]["EN"] == message.validAnswer){
				italianAnswer = message.dict[i]["IT"];
			}
		}
		feedback = t2 + italianAnswer + validAnswerTextFromJSON;
		background = "Red";
	}

	$(".answered").css("background-color", background);
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
