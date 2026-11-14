extends Node
## Enter this scene when the story is complete; it chooses and plays the
## ending automatically from the current saved story flags.

const EndingSelector = preload("res://scripts/ending_selector.gd")
const ENDINGS_PATH := "res://data/dialogue/endings.json"


func _ready() -> void:
	var dialogue_box := preload("res://scenes/ui/dialogue_box.tscn").instantiate()
	add_child(dialogue_box)
	DialogueManager.dialogue_finished.connect(_on_ending_finished, CONNECT_ONE_SHOT)
	var entry: String = EndingSelector.select_ending(GameState.flags)
	if not DialogueManager.start(ENDINGS_PATH, entry):
		push_error("Could not start ending dialogue: %s" % entry)


func _on_ending_finished() -> void:
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
