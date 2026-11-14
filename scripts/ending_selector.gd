extends RefCounted
## Select an ending from the final story flags. No reading (or contradictory
## legacy readings) falls back to the ambiguous ending.

static func select_ending(flags: Dictionary) -> String:
	var skeptic := flags.get("skeptic", false) == true
	var believer := flags.get("believer", false) == true
	if skeptic == believer:
		return "keep_the_light"
	var trusts_edith := flags.get("trusted_edith", false) == true
	if believer:
		return "edith_vindicated" if trusts_edith else "light_believed_edith_doubted"
	return "keep_the_light" if trusts_edith else "explained_away"
