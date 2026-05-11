# CodiePet Quality Checks

## Source image checks

Accept the source image only when it appears to contain one clear human subject. Ask for a replacement if the image contains multiple prominent people, a pet, an object, scenery, a heavily blocked face, a very small person, a back view, or an extreme side view.

## Character preview checks

The preview passes when it is one full-body Q-style character, keeps the source person's recognizable traits, has a white or transparent background, and has no labels or scenery.

## State strip checks

A state strip passes when it is one horizontal row, contains exactly four frames, keeps the same character identity across frames, includes no labels or grid lines, and has no cropped body parts or props.

## Final pack checks

The final pack passes when all six GIFs exist, each state has four PNG frames, `avatar.config.json` exists, and at least one preview file exists under `codie-pet/previews/`.
