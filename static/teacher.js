$(document).ready(function () {
	//~ get list of exercises types
	ask_info("exercises_types");
});

function ask_info(what, data) {
	if (what == "logged") {
		$.get("/dashboard/get_logged");
	}
	else if (what == "exercises_types") {
		$.get("/dashboard/exercises_types/list");
	}
	else if (what == "exercises_list") {
		$.get("/dashboard/exercises_list/" + data);
	}
}

onMessage = function (message) {
	var data = JSON.parse(message.data);
	if (data.type == "exercises_types") {
		build_types_choice(data.message);
	}
	else if (data.type == "exercises_list") {
		build_exercises_list(data.message);
	}
	//~ mylog(data);
}

function build_types_choice(data) {
	for (var i =0; i < data.length; i++) {
		var b = $(document.createElement("button"))
			.attr("class", "exercise_type")
			.text("List for " + data[i].name);
		$("#exercises_menu").append(b);
		$(b).on("click", {id: data[i].id}, button_fired);
	}
}

function build_exercises_list(exercises_list) {
	$("#exercise_list").remove();
	var list = $(document.createElement("div"))
		.attr("id", "exercise_list");
	var exercise = "<div id='exercise_list_title'>List of available exercises</div>";
	for (var i = 0; i < exercises_list.length; i++) {
		exercise += "<div class='sentence' id='" + i;
		exercise += "'>" + exercises_list[i].sentence + "</div> ";
	}
	$("#exercise_list").append(exercise);
	var type = $(document.createElement("div"))
			.attr("class", "hidden")
			.attr("id", "exercise_type")
			.text(exercises_list[0].type);
	$(list).append(type);
	$("#exercises_menu").append(list);
	$(".sentence").on("click", sentence_t_clicked);
}

function button_fired (event) {
	if ($(event.target).hasClass("exercise_type")) {
		ask_info("exercises_list", event.data.id);
	}
}
