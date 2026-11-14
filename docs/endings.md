# Ending graph

`data/dialogue/endings.json` contains four independent entry points, each
ending with `next: null`. They are narrative drafts based on the four outcomes
in the narrative flags-and-branches design document.

| Entry point | Outcome |
| --- | --- |
| `explained_away` | The keeper explains the light as a distant vessel while leaving some uncertainty. |
| `edith_vindicated` | The light is believed and Edith's account is vindicated. |
| `light_believed_edith_doubted` | The light is real, but Edith's interpretation remains in doubt. |
| `keep_the_light` | The keeper accepts uncertainty and continues tending the light. |

These are entry points, not a flag-to-ending selector. The design calls for
reading × trust, but `trusted_edith` currently records the logbook choice to
radio the mainland or keep quiet, not an explicit judgment of Edith's
credibility. The mapping of skeptic/trust combinations to the explained-away
and ambiguous endings also remains undecided. Do not route from
`trusted_edith` until that meaning and the full four-cell mapping are agreed.
An unset or contradictory belief needs an explicit policy too.

The existing DialogueManager does not evaluate conditions or branch on
`radioed_tom`. The design calls for that flag to color the epilogue, but
neither ending selection nor Tom-specific epilogue variants are implemented
here. Once the design is settled, the calling scene must choose an entry ID
and start the graph; test all four routes and both radio states in Godot.
