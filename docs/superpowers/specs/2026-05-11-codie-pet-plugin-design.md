# CodiePet Plugin v0.1 Design

## Summary

CodiePet Plugin v0.1 is a local Codex plugin that lets a user turn one clear single-person photo into a Q-style animated avatar pack for Codex chats.

The plugin does not run a cloud service and does not modify the Codex desktop UI. It provides a guided skill workflow, local scripts for deterministic asset processing, and workspace rules that make Codex naturally insert state GIFs in replies.

The first version uses a fixed Q-style desktop-pet visual style, supports one person per source image, requires user confirmation of the character preview, and generates six core state GIFs.

## Goals

- Let a non-technical user start from one single-subject human photo.
- Generate a Q-style avatar character preview before any GIF pack work.
- Require explicit user approval of the character preview.
- Generate six avatar states for common Codex work phases:
  - `idle`
  - `peek`
  - `loading`
  - `coding`
  - `error`
  - `done`
- Store generated assets in the current workspace.
- Install workspace-local response rules into `AGENTS.md`.
- Use relative local GIF paths so the workspace remains portable.
- Keep the plugin local and script-driven for v0.1.

## Non-Goals

- No cloud generation service.
- No account system, quota system, billing, or remote storage.
- No direct modification of the Codex desktop client UI.
- No floating desktop pet overlay outside Markdown replies.
- No global cross-workspace auto-install.
- No multi-person photos.
- No pet, object, scenery, or non-human source images.
- No user-selectable visual styles in v0.1.
- No promise that every assistant message will always contain a GIF; user, system, and developer instructions still take priority.

## User Input Scope

v0.1 supports one clear single-subject human photo.

The skill should ask for a replacement image when:

- The image contains more than one prominent person.
- The person is too small in the frame.
- The face or upper body is heavily blurred, blocked, or cropped.
- The image is mostly a back view or extreme side view.
- The image is a pet, object, landscape, logo, or abstract image.

The user-facing wording should be direct:

```text
Please upload a clear single-person photo. v0.1 works best with a front-facing or near-front-facing person where the hair, face, and upper body are visible.
```

## Fixed Visual Style

The first version uses one fixed style:

- Cute Q-style anime desktop pet.
- 2 to 2.5 head-body ratio.
- Large head, small body, clear facial expression.
- Clean dark outline.
- Flat cel-shaded coloring.
- No realistic portrait rendering.
- No painterly or 3D clay style.
- White or transparent background.
- Readable when displayed small in a chat reply.

The generated character should preserve the source person's most recognizable traits:

- Hair shape and color.
- Face impression.
- Clothing style and dominant clothing colors.
- Glasses, hat, earrings, or other prominent accessories.
- Overall personality impression.

The plugin should not promise photo-real likeness. It should frame the output as a cute Q-style version inspired by the photo.

## Core Workflow

```text
User uploads a single-person photo
  -> CodiePet skill validates the input scope
  -> Codex generates one Q-style character preview
  -> User confirms, regenerates, or adds correction notes
  -> Codex generates six independent state strips
  -> build_avatar_pack.py slices frames and builds GIFs
  -> validate_avatar_pack.py checks required outputs
  -> preview assets are created
  -> User confirms installation
  -> install_avatar_rules.py updates AGENTS.md
  -> Future Codex replies can use local state GIFs
```

## Required User Confirmation

The character preview confirmation is mandatory. The workflow must not generate state strips until the user approves the preview.

The confirmation choices are:

```text
1. Use this character
2. Regenerate with the same style
3. Regenerate with corrections
```

Correction examples:

- "Keep the glasses more visible."
- "Make the hair longer."
- "Use a black hoodie."
- "Make the expression softer."
- "Keep the same bangs as the photo."

## State Set

v0.1 generates six states.

| State | Use Case | Animation Beat |
| --- | --- | --- |
| `idle` | General chat, thinking, lightweight answers | Standing, blinking, slight smile or nod |
| `peek` | Reading files, inspecting context, checking previews | Peeking from a window edge or screen edge |
| `loading` | Running commands, waiting, long tasks | Holding or hugging a progress bar |
| `coding` | Writing code, editing files, generating assets | Typing on a tiny keyboard or laptop |
| `error` | Failed command, failed test, blocked state | Holding an `ERROR` sign or shrugging |
| `done` | Successful final result | Celebrating with confetti or `100%` |

Each state is generated as one independent horizontal strip with exactly four frames.

## Why Independent State Strips

Each state is generated separately instead of one large six-row image.

This lowers cost when one state fails, because only the failed state needs regeneration. It also makes quality review simpler: the user and Codex can inspect one action at a time, and the local scripts can report exactly which state has an issue.

## State Strip Requirements

Each state strip must meet these requirements:

- Exactly one horizontal row.
- Exactly four frames.
- One character only.
- Same character identity across frames.
- Same outfit, hairstyle, color palette, and proportions.
- No frame labels.
- No grid lines.
- No borders.
- No extra characters.
- No scenery.
- White or transparent background.
- No cropped hair, head, hands, feet, body, or action props.
- Enough spacing between frames for reliable slicing.

## Plugin Package Structure

```text
plugins/codie-pet/
  .codex-plugin/
    plugin.json
  skills/
    codie-pet/
      SKILL.md
      references/
        workflow.md
        prompts.md
        quality-checks.md
  scripts/
    build_avatar_pack.py
    install_avatar_rules.py
    uninstall_avatar_rules.py
    validate_avatar_pack.py
  assets/
    icon.png
    icon-small.svg
```

## Workspace Output Structure

The generated avatar pack is stored inside the user's current workspace:

```text
codie-pet/
  source/
    original.png
    character-preview.png
  strips/
    idle.png
    peek.png
    loading.png
    coding.png
    error.png
    done.png
  frames/
    idle/
      frame-01.png
      frame-02.png
      frame-03.png
      frame-04.png
    peek/
    loading/
    coding/
    error/
    done/
  gifs/
    idle.gif
    peek.gif
    loading.gif
    coding.gif
    error.gif
    done.gif
  previews/
    contact-sheet.png
    preview.html
  avatar.config.json
```

## Avatar Config

`avatar.config.json` records the generated pack and state mapping.

```json
{
  "version": 1,
  "style": "q-chibi",
  "frameCount": 4,
  "states": {
    "idle": {
      "label": "Idle",
      "gif": "./gifs/idle.gif",
      "useWhen": "General chat, thinking, lightweight answers"
    },
    "peek": {
      "label": "Peek",
      "gif": "./gifs/peek.gif",
      "useWhen": "Reading files, inspecting context, checking previews"
    },
    "loading": {
      "label": "Loading",
      "gif": "./gifs/loading.gif",
      "useWhen": "Running commands, waiting, long tasks"
    },
    "coding": {
      "label": "Coding",
      "gif": "./gifs/coding.gif",
      "useWhen": "Writing code, editing files, generating assets"
    },
    "error": {
      "label": "Error",
      "gif": "./gifs/error.gif",
      "useWhen": "Failed commands, failed tests, blocked work"
    },
    "done": {
      "label": "Done",
      "gif": "./gifs/done.gif",
      "useWhen": "Successful final results"
    }
  }
}
```

Paths inside `avatar.config.json` are relative to the `codie-pet/` directory.

## Skill Responsibilities

`skills/codie-pet/SKILL.md` owns the user-facing workflow.

It should:

- Trigger when the user asks to create, install, regenerate, disable, or remove a CodiePet.
- Enforce the v0.1 input scope.
- Ask for a clear single-person photo when no image is provided.
- Generate the character preview prompt.
- Require user confirmation before state generation.
- Generate state strip prompts one state at a time.
- Tell Codex to save generated strips under `codie-pet/strips/`.
- Run scripts after required assets exist.
- Explain failures in actionable language.
- Avoid claiming direct UI injection.

## Script Responsibilities

### `build_avatar_pack.py`

Inputs:

- `codie-pet/strips/*.png`
- Optional state config arguments.

Responsibilities:

- Verify all six required strip files exist.
- Slice each horizontal strip into exactly four frames.
- Normalize frame canvas sizes within each state.
- Save frames under `codie-pet/frames/<state>/`.
- Build looping GIFs under `codie-pet/gifs/`.
- Generate `avatar.config.json`.
- Generate `previews/contact-sheet.png`.
- Generate `previews/preview.html`.

Implementation notes:

- Use Pillow for image IO and GIF generation.
- Default GIF frame duration: 180 ms.
- Default loop: infinite.
- Use nearest reasonable crop/slice strategy for equal-width strips.
- Fail with clear messages when an image is missing or has invalid dimensions.

### `validate_avatar_pack.py`

Responsibilities:

- Check required directories.
- Check all six GIFs exist.
- Check all six state frame folders contain exactly four PNGs.
- Check `avatar.config.json` is valid JSON.
- Check `preview.html` exists.
- Print a short pass/fail report.

### `install_avatar_rules.py`

Responsibilities:

- Create `AGENTS.md` if it does not exist.
- Preserve existing `AGENTS.md` content.
- Insert or replace only the `codie-pet` managed block.
- Use relative paths from the workspace root.
- Avoid duplicate blocks.

### `uninstall_avatar_rules.py`

Responsibilities:

- Remove only the `codie-pet` managed block from `AGENTS.md`.
- Preserve all other `AGENTS.md` content.
- Leave generated assets in place by default.
- Support an optional flag to remove the `codie-pet/` asset directory later if needed.

## Managed AGENTS.md Block

The install script writes this managed block:

```md
<!-- codie-pet:start -->
## CodiePet GIF Response Style

Use local avatar GIFs from `./codie-pet/gifs/` when replying in this workspace.

- Use `idle.gif` for general chat, thinking, and lightweight answers.
- Use `peek.gif` when reading files, inspecting context, or checking previews.
- Use `loading.gif` when running commands, waiting, processing, or doing long tasks.
- Use `coding.gif` when writing code, editing files, generating assets, or implementing changes.
- Use `error.gif` when a command fails, tests fail, or work is blocked.
- Use `done.gif` for successful final responses and clean completion.

Placement rules:
- Put the selected GIF near the beginning of short replies.
- During long-running work, include the current-state GIF in progress updates when useful.
- Do not explain the GIF system every time; use it naturally.

Selection rules:
- Choose the GIF from the current task stage.
- If several states apply, choose the most active current state.
- If the user asks to remove, reduce, or change avatar behavior, follow the user.
- User, system, and developer instructions take priority over these avatar rules.
<!-- codie-pet:end -->
```

## Prompt Strategy

The skill uses two prompt families.

### Character Preview Prompt

Purpose:

- Convert the uploaded person into one Q-style desktop-pet character.
- Lock identity before animation work begins.

Key constraints:

- One character.
- Q-style anime desktop pet.
- Preserve major personal features.
- White or transparent background.
- Full body visible.
- No text labels.
- No scenery.

### State Strip Prompt

Purpose:

- Generate one four-frame horizontal action strip for one approved character.

Key constraints:

- Use the approved character preview as identity reference.
- Same character in all frames.
- Exactly four frames.
- Horizontal strip.
- No grid lines or labels.
- No cropped body parts or props.
- White or transparent background.

The prompts should live in `skills/codie-pet/references/prompts.md` so they can be refined without changing script code.

## Error Handling

The workflow should handle these cases:

| Case | Behavior |
| --- | --- |
| No image provided | Ask the user to upload one clear single-person photo |
| Invalid source image | Explain the v0.1 input limits and request a replacement |
| Character preview rejected | Offer regenerate or regenerate with corrections |
| One state strip is bad | Regenerate only that state |
| Missing strip file | `build_avatar_pack.py` reports the missing file and stops |
| Wrong frame count | Re-run generation for the affected state |
| Pillow missing | Script explains how to install the dependency |
| Existing `AGENTS.md` | Preserve it and update only managed block |
| User cancels before install | Keep generated assets, do not write rules |

## Privacy and Consent

Because v0.1 handles human photos, the skill should be explicit:

- The user must have the right to use the uploaded photo.
- The plugin stores generated assets in the current local workspace.
- v0.1 does not add a cloud upload step.
- The plugin should not use the image for examples, training, or sharing.

## Testing Strategy

Script-level tests should cover:

- Slicing a synthetic four-frame strip.
- Building all six GIFs from fixture strips.
- Failing clearly when a required strip is missing.
- Failing clearly when a strip cannot be opened.
- Writing `avatar.config.json`.
- Installing the managed `AGENTS.md` block into an empty file.
- Replacing an existing managed block without duplicating it.
- Preserving unrelated `AGENTS.md` content.
- Removing only the managed block.

Manual workflow verification should cover:

- A valid single-person photo flow.
- Rejected character preview and regeneration.
- Rejected single state strip and state-only regeneration.
- Final GIF display through Markdown local paths.
- A new Codex session reading the workspace rules.

## Acceptance Criteria

v0.1 is complete when:

- The plugin manifest is valid.
- The `codie-pet` skill triggers for avatar creation and installation requests.
- The workflow requires character preview confirmation.
- The scripts generate six GIFs from six four-frame strips.
- The workspace output structure matches this design.
- `avatar.config.json` is generated.
- `preview.html` or `contact-sheet.png` is generated.
- `AGENTS.md` is updated with a single managed block.
- Existing `AGENTS.md` content is preserved.
- The uninstall script removes only the managed block.
- Verification commands pass for the script layer.

## Implementation Notes

- The actual image generation call is handled by Codex's available image generation capability, guided by the skill. Scripts do not call a model API in v0.1.
- The first implementation can use equal-width slicing for each strip. More advanced object-boundary normalization can be added after the basic workflow is reliable.
- If Codex cannot save generated images directly into the target paths in a given environment, the skill should ask the user to place the generated files under `codie-pet/strips/` before running `build_avatar_pack.py`.
