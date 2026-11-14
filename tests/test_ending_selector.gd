extends SceneTree

const Selector = preload("res://scripts/ending_selector.gd")


func _initialize() -> void:
	var cases := [
		[{"skeptic": true, "believer": false, "trusted_edith": false}, "explained_away"],
		[{"skeptic": true, "believer": false, "trusted_edith": true}, "keep_the_light"],
		[{"skeptic": false, "believer": true, "trusted_edith": false}, "light_believed_edith_doubted"],
		[{"skeptic": false, "believer": true, "trusted_edith": true}, "edith_vindicated"],
		[{}, "keep_the_light"],
		[{"skeptic": false, "believer": false, "trusted_edith": true}, "keep_the_light"],
		[{"skeptic": true, "believer": true, "trusted_edith": true}, "keep_the_light"],
		[{"believer": true}, "light_believed_edith_doubted"],
	]
	var failed := false
	for item in cases:
		var actual: String = Selector.select_ending(item[0])
		if actual != item[1]:
			printerr("Expected %s, got %s for %s" % [item[1], actual, item[0]])
			failed = true
	quit(1 if failed else 0)
