$(document).ready(function () {
	//~ get list of exercises types
	ask_info("exercises_types");
});

function ask_info(what, data) {
	if (what == "logged") {
		$.get("/dashboard/get_logged");
	}
	else if (what == "exercises_types") {
		$.get("/dashboard/exercises_types");
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

function button_fired (event) {
	if ($(event.target).hasClass("exercise_type")) {
		ask_info("exercises_list", event.data.id);
	}
}
