# Ending selection

The game selects an entry in `data/dialogue/endings.json` from the
current belief and trust flags. The logbook's choice to share Edith's account
means the player takes it at face value; keeping it quiet means they do not.

| Reading | `trusted_edith` | Ending entry |
| --- | --- | --- |
| skeptic | false | `explained_away` |
| skeptic | true | `keep_the_light` |
| believer | false | `light_believed_edith_doubted` |
| believer | true | `edith_vindicated` |

The skeptic/trust mapping assigns the ambiguous ending to trusting Edith while
explaining the light away; the other skeptic corner explains it away. If neither
reading is true, or an old inconsistent state has both true, the selector
returns `keep_the_light`. An absent trust flag defaults to false, matching
`GameState.get_flag` behavior. `radioed_tom` does not change the selection;
Tom-specific epilogue coloring is not implemented.

`scenes/ending.tscn` selects and starts the ending automatically in
`_ready()`, then returns to the main menu when dialogue finishes. The fork
currently has no end-of-story event: the lamp room is an unconnected scaffold
and the stair ends in placeholder dialogue. When the final story beat exists,
transition once to `res://scenes/ending.tscn`. Do not attach it to the demo
stair or logbook completion, which would end the story prematurely.

Run `godot --headless --path . --script res://tests/test_ending_selector.gd`
to check the matrix, then test the scene and save/load behavior in the engine.
