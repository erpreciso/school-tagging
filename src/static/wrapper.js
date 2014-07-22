$(document).ready(function(){
	$(".language").on("click", function(event){
		var p = event.target.innerText;
		$.post("/language", {"language": p});
		$("#language_switch").append("Please refresh to see changes");
	});
});

function getLanguage() {
	return $("#language_switch .current").text();
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
			.css("background-color", "red"));
}