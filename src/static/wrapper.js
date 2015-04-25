// school-tagging --> an educative Student / Classroom 
//    Response Systems designed to help teaching and merge into 
//    academic research.
//    Copyright (C) 2014  Stefano Merlo, Federico Sangati, Giovanni Moretti.
// This program comes with ABSOLUTELY NO WARRANTY.
// This is free software, and you are welcome to redistribute it 
// under certain conditions (i.e. attribution); for details refer 
//     to 'LICENSE.txt'.

$(document).ready(function(){
	$(".language").on("click", function(event){
		var p = event.target.innerText;
		$.post("/language", {"language": p});
		$("#language_switch").append("Please refresh to see changes");
	});
});

function getLanguage() {
	//return $("#language_switch .current").text();
	return "IT";
}

function askMeRefresh () {
	var language = getLanguage();
	if (language == "EN") {
		var t1 ="Please refresh this page";
	}
	else if (language == "IT") {
		var t1 = "Pregasi aggiornare la pagina tramite l'apposito comando nel menù di navigazione";
	}
	$("#lessonName").after($(document.createElement("div"))
			.text(t1)
			.css("color", "red"));
}
