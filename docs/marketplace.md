# CodiePet Marketplace Metadata

This repository uses a repo-local Codex plugin marketplace at `.agents/plugins/marketplace.json`.

The marketplace and plugin manifest shapes follow the local Codex `plugin-creator` reference available in this development environment as of 2026-05. If Codex publishes a public JSON Schema, validate these files against that schema before release.

Current assumptions:

- `marketplace.json` lives at `<repo-root>/.agents/plugins/marketplace.json`.
- `plugins[].source.path` is relative to the marketplace root and points to `./plugins/codie-pet`.
- `policy.installation` accepts `NOT_AVAILABLE`, `AVAILABLE`, or `INSTALLED_BY_DEFAULT`.
- `policy.authentication` accepts `ON_INSTALL` or `ON_USE`.
- Plugin UI metadata lives in `plugins/codie-pet/.codex-plugin/plugin.json`.

Manual validation commands:

```bash
python3 -m json.tool .agents/plugins/marketplace.json
python3 -m json.tool plugins/codie-pet/.codex-plugin/plugin.json
```
