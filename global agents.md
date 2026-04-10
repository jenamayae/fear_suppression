## purpose
global rules for coding assistants. governs style, edits, and refactoring. project-specific rules go in local agents.md.

## priorities
- preserve scientific validity, inspectability, and refactorability
- explicit, simple, auditable code
- reuse libraries when clearer

## output
- do not directly apply edits unless explicitly asked
- provide clean copy-paste edits for inspection first
- requests for help do not imply permission to edit files directly
- after proposing edits, ask whether to implement them
- if logic changes enables clean up, suggest separate edit

## avoid
- abstraction unless it clearly improves clarity or reduces real redundancy
- class-heavy design
- hidden state
- abstractions hiding condition logic
- large rewrites over small patches
- mixing cleanup with logic 
- buried parameters
- verbose comments/docstrings
- inconsistent naming/order/units

## organization
- simple file roles (stimuli, trials, utils, hardware, experiment, main)
- keep logic locally understandable
- helpers directly below parent function; shared at bottom or utils
- keep parameters explicit and near top

## style
- prefer explicit over clever
- similar code looks similar
- concise names; include units (e.g., center_radius_cm)
- booleans clearly indicate meaning (is/has/can/should/need)
- conservative renaming only
- no uppercase unless required externally
- preserve ordering of related variables
- conditionals: changing variable first

## comments
- for non-obvious logic or reasoning
- include brief rationale or example values if useful
- write so comments can be deleted later
- prefer comments; use tiny tests at checkpoints

## local agents
local agents.md defines experiment-specific rules (stimuli, timing, logging, hardware, validation).

