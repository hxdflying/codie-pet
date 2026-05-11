# CodiePet Privacy

CodiePet stores generated assets in the current workspace under `codie-pet/`.

The plugin scripts do not add an additional upload step. Image generation is performed by Codex's own image-generation capability, which may send the attached photo and generated prompts to a cloud-hosted model operated by the Codex provider. CodiePet does not control that processing path.

Workspace files may include:

- `codie-pet/source/original.png`
- `codie-pet/source/character-preview.png`
- `codie-pet/strips/*.png`
- `codie-pet/frames/**/*.png`
- `codie-pet/gifs/*.gif`
- `codie-pet/previews/*`
- `codie-pet/avatar.config.json`

Only use photos you have the right to use. Delete `codie-pet/` from the workspace if you no longer want to keep the generated assets.
