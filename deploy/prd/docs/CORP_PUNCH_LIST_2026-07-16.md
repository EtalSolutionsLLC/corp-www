# Corporate Website Punch List — 2026-07-16

Status: Active  
Scope: Et al Solutions corporate website, Systems Lab  
Source: Local review findings recorded 2026-07-16

## CORP-2026-07-16-001 — Add conventional keyboard submission to the capability matcher

Status: Open  
Priority: High

### Finding

The local capability-match textarea requires a pointer click on **Run the local model**. It does not provide the conventional chat-style keyboard interaction.

### Decision

- `Enter` submits the current prompt.
- `Shift+Enter` inserts a newline.
- An empty or whitespace-only prompt does not submit.
- Input Method Editor composition must not trigger submission while composition is active.
- The visible button remains available for pointer, touch, keyboard, and assistive-technology users.

### Acceptance criteria

1. Pressing `Enter` with non-empty text runs the matcher exactly once.
2. Pressing `Shift+Enter` inserts a newline and does not run the matcher.
3. Pressing `Enter` during active IME composition does not run the matcher.
4. Empty input retains the existing validation message.
5. Automated tests cover submission, newline insertion, IME composition, and empty input.

## CORP-2026-07-16-002 — Remove blocking browser-model inference from the public tool

Status: Open  
Priority: Critical

### Finding

The tool dynamically imports Transformers.js, downloads and initializes `Xenova/all-MiniLM-L6-v2`, and performs sentence-embedding inference in the browser. On the reviewed local system it is very slow and makes the site appear frozen while the model loads and runs.

The current implementation already contains a deterministic capability matcher named `keywordFallback`, but it is used only after model failure.

### Decision

Do not retain the current browser-model implementation in the public experience. Promote the deterministic local matcher to the primary implementation and remove the public Transformers.js/model-loading path. This capability-selection task does not justify a large model download, long initialization, or an unresponsive page.

If semantic model matching is reconsidered later, it must run outside the main browser thread and meet an explicit nonblocking contract: worker isolation, cached capability vectors, visible progress, cancellation, timeout, failure recovery, and measured responsiveness on representative low-power hardware.

### Acceptance criteria

1. Running the capability matcher does not request Transformers.js or a model artifact.
2. The page remains responsive to scrolling, navigation, typing, and dismissal while matching runs.
3. The matcher returns a deterministic result from the published capability contract.
4. Public labels no longer claim that a language model is running.
5. The privacy statement remains accurate: submitted text is processed locally and is not transmitted.
6. Automated tests verify the deterministic match, absence of model loading, visible status, and error handling.

