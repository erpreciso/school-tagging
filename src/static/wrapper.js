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