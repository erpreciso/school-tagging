$(document).ready(function () {
	$(".buttons .exercise_type").on("click", function (event) {
		mylog(event.target.id);
		mylog(event.target.parentNode.parentNode.id);
	});
});
