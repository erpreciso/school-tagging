// school-tagging --> an educative Student / Classroom 
//    Response Systems designed to help teaching and merge into 
//    academic research.
//    Copyright (C) 2014  Stefano Merlo, Federico Sangati, Giovanni Moretti.
// This program comes with ABSOLUTELY NO WARRANTY.
// This is free software, and you are welcome to redistribute it 
// under certain conditions (i.e. attribution); for details refer 
//     to 'LICENSE.txt'.

$(document).ready(function(){
        importLanguageJSON();
	$(".language").on("click", function(event){
		var p = event.target.innerHTML;
		$.post("/language", {"language": p});
		$("#language_switch").append("Please refresh to see changes");
	});
});

function importLanguageJSON () {
        localStorage.removeItem("language_dictionary");
	$.get("/get_language_dict");

}

function getLanguage() {
	return $("#language_switch .current").text();
//	return "IT";
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

onMessage = function(message) {
	var language = getLanguage();
	var data = JSON.parse(message.data);
        if (data.type == "languageDictionary"){
                localStorage.setItem("language_dictionary", JSON.stringify(data.message));
                afterDictionaryReceived();
        }
        manageMessage(data, language);
}

function languageDict () {
        return(JSON.parse(localStorage.getItem("language_dictionary")));
}

