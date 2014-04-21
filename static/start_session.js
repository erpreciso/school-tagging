$(document).ready(function () {
	$(".buttons .exercise_type").on("click", function (event) {
		var param = {
				"type": event.target.id,
				"id": event.target.parentNode.parentNode.id,
			};
		$.post("/session/exercise_request", param);
	});
});
