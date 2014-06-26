$(document).ready(function() {
	$("#show_html").on("click", loghtml);
});

onOpened = function() {
	$("#connection_status").text("ONLINE")
	.css("color", "green");
	}

onClose = function() {
	$("#connection_status")
		.text("OFFLINE")
		.css("color", "red");
	}

function mylog(message) {
	if (window.console && window.console.log) {
		console.log(message);
	}
}

function loghtml(){
	mylog($("body").html());
}
