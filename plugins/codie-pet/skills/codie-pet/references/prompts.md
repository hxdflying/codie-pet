# CodiePet Prompt Templates

## Character preview prompt

Use the uploaded single-person photo as the identity reference. Create one cute Q-style anime desktop-pet character.

Hard requirements:

- One character only.
- Preserve recognizable features from the photo: hair shape, hair color, face impression, clothing style, dominant clothing colors, glasses, hat, earrings, and prominent accessories.
- Q-style anime desktop pet, 2 to 2.5 head-body ratio.
- Large head, small body, clear facial expression.
- Clean dark outline and flat cel-shaded colors.
- Full body visible.
- White background.
- No labels, no frame numbers, no border, no scenery.
- Do not render a realistic portrait.

Generate a single full-body character preview image.

## State strip prompt template

Use `codie-pet/source/character-preview.png` (the approved Q-style character preview) as the identity reference. Generate one horizontal four-frame animation strip for state: `<STATE>`.

Hard requirements:

- Exactly four frames.
- One horizontal row.
- Same character in every frame.
- Same outfit, hairstyle, color palette, proportions, and accessories.
- Enough spacing between frames for slicing.
- White background.
- No labels, no frame numbers, no grid lines, no borders.
- No extra characters.
- Do not crop hair, head, hands, feet, body, or props.

Animation beat for `<STATE>`:

- `idle`: standing, blinking, slight smile or nod.
- `peek`: peeking from a window edge or screen edge.
- `loading`: holding or hugging a progress bar while waiting.
- `coding`: typing on a tiny keyboard or laptop.
- `error`: holding an ERROR sign or shrugging with a blocked expression.
- `done`: celebrating with confetti or a 100% sign.
