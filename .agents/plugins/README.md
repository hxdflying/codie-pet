# Local Codex Marketplace

This directory holds a repo-local plugin marketplace so you can install CodiePet during development without publishing it. Codex desktop loads it via:

```bash
codex plugin marketplace add .
```

## Schema provenance

`marketplace.json` and `plugins/codie-pet/.codex-plugin/plugin.json` use field shapes observed in Codex desktop's plugin system as of 2026-05. They are **not** validated against a published JSON schema in this repository because Anthropic has not yet shipped one for community use. Fields are believed to be:

- **`name`**: stable identifier for the marketplace; lowercase, hyphenated.
- **`interface.displayName`**: shown in the plugin picker UI.
- **`plugins[]`**: one entry per plugin offered by this marketplace.
- **`plugins[].source.source`**: `"local"` for a local path (the only form used here).
- **`plugins[].source.path`**: path to the plugin directory relative to this `marketplace.json`.
- **`plugins[].policy.installation`**: `"AVAILABLE"` makes the plugin installable from the picker but not auto-installed. `"REQUIRED"` (if supported) would auto-install.
- **`plugins[].policy.authentication`**: `"ON_INSTALL"` means the user confirms install once; later uses do not re-prompt.
- **`plugins[].category`**: free-form string surfaced in the picker.

If a future release of Codex publishes an official schema, validate this file against it and prune any obsolete fields.

## Failure modes

If `codex plugin marketplace add .` succeeds but CodiePet does not appear under "CodiePet Local" in the plugin picker, check:

1. The `path` in `source.path` resolves to the actual plugin directory (must contain `.codex-plugin/plugin.json`).
2. `plugin.json` parses as valid JSON (`python3 -m json.tool plugins/codie-pet/.codex-plugin/plugin.json`).
3. Codex desktop has been restarted after `marketplace add`.
4. The plugin is enabled in the desktop app's plugin settings.
