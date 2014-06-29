$(document).ready(function () {
	$("#startExercise").on("click", startExercise);
	
});

onMessage = function(message) {
	var data = JSON.parse(message.data);
	if (data.type == "student arrived") {
		var studentName = data.message.studentName;
		var studentsCount = $(".studentName").length;
		var txt = (studentsCount + 1).toString() + ". " + studentName;
		var student = $(document.createElement("div"))
			.attr("id", studentName)
			.addClass("studentName")
			.text(txt);
		$("#students").append(student);
	}
	else if (data.type == "student logout") {
		//~ console.log("hit");
		$("#" + data.message.studentName).remove();
	}
	else if (data.type == "exercise to solve") {
		console.log(data.message);
		
	}
}

onOpened = function(){};

startExercise = function () {
	$.get("/data/exercise_request");
};
