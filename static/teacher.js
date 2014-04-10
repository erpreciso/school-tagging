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
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercises_types") {
		Dashboard.build_buttons_to_choose(data_arrived.message);
	}
	else if (data_arrived.type == "exercises_list") {
		var list = data_arrived.message;
		var exercise_type = data_arrived.exercise_type;
		Dashboard.build_exercises_list(list, exercise_type);
	}
	else if (data_arrived.type == "exercise") {
		var exercise = data_arrived.message;
		Dashboard.add_exercise_to_all_students_dashboards(exercise);
	}
	else if (data_arrived.type == "connected_user") {
		var student = data_arrived.username;
		Dashboard.add_student_dashboard(student);
	}
	else if (data_arrived.type == "disconnected_user") {
		var student = data_arrived.username;
		Dashboard.remove_student_dashboard(student);
	}
}

var Dashboard = {
	build_buttons_to_choose: function (data) {
		var types = data;
		for (var i =0; i < types.length; i++) {
			var button = $(document.createElement("button"))
				.attr("class", "exercise_type")
				.attr("id", "choose_type_" + i)
				.text("List for " + types[i].name);
			$("#exercises_menu").append(button);
			$(button).on("click", {type: types[i].id}, function (event) {
				ask_info("exercises_list", event.data.type);
			});
		}
	},
	add_student_dashboard: function (student) {
		var student_dashboard = $(document.createElement("div"))
			.attr("class", "student_dashboard")
			.attr("id", student);
		var name = $(document.createElement("div"))
			.attr("class", "name")
			.text(student);
		var exercise_content = $(document.createElement("div"))
			.attr("class", "exercise_content");
		var exercise_status = $(document.createElement("div"))
			.attr("class", "exercise_status");
		var response_time = $(document.createElement("div"))
			.attr("class", "response_time");
		$(student_dashboard)
			.append(name)
			.append(exercise_content)
			.append(exercise_status)
			.append(response_time);
		$("#students_data").append(student_dashboard);
	},
	remove_student_dashboard: function (student) {
		$("#" + student).remove();
	},
	build_exercises_list: function (exercises_list, exercise_type) {
		//~ $("#exercises_list").remove();
		var list = $(document.createElement("div"))
			.attr("id", "exercises_list");
		for (var i = 0; i < exercises_list.length; i++) {
			var sentence = $(document.createElement("div"))
				.attr("class", "sentence")
				.attr("id", "sentence_" + i)
				.text(exercises_list[i].sentence);
			$(list).append(sentence);
		}
		var button = $(document.createElement("button"))
			.attr("id", "send_exercise_choosen")
			.text("Send exercise to classroom");
		$("#exercises_menu")
			.append(list)
			.append(button);
		$(list).on("click", Dashboard.choose_element);
		$(button).on("click", {type: exercise_type}, function(event) {
			var chosen = $("#chosen").parent().attr("id").substring(9);
			param = {"exercise_number": chosen, "type": event.data.type}
			$.post("/dashboard/exercise_request/foo", param);
		});
	},
	choose_element: function (event) {
		//~ on click, will highlight the element clicked and add a nested 
		//~ element with id=chosen
		var triggered = $("#" + event.target.id);
		var container = $(triggered).parent();
		$(container).children().css("background-color", "inherit");
		$(triggered).css("background-color", "yellow");
		$("#chosen").remove();
		var chosen = $(document.createElement("div"))
			.attr("id", "chosen")
			.attr("class", "hidden");
		$(triggered).append(chosen);
	},
	add_exercise_to_all_students_dashboards: function (exercise) {
		//~ mylog(exercise);
		var students_count = $(".student_dashboard").length;
		for (var i = 0; i < students_count; i++) {
			var sentence = $(document.createElement("div"))
				.attr("class", "sentence")
				.text(exercise.sentence);
			$($(".student_dashboard")[i])
				.children(".exercise_content")
				.append(sentence);
			
		}
	}
}
