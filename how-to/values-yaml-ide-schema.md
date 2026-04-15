---
title: IDE autocomplete and validation for values.yaml
nav_order: 10
parent: How to...
domain: public
permalink: /values-yaml-ide-schema
last_reviewed_on: 2026-04-15
review_in: 6 months
---

# IDE autocomplete and validation for values.yaml

Bind the published JSON Schema for an IDP Helm chart to your `values.yaml` and get autocomplete, inline validation, and hover descriptions directly in your editor — the same checks Helm runs at install time, just several keystrokes earlier.

## What you get

- **Autocomplete** for every valid key under the cursor.
- **Inline error markers** on invalid values (wrong type, unknown key when `additionalProperties: false`, value outside an `enum`).
- **Hover tooltips** with the field description sourced from the chart's `values.yaml`.

## Prerequisites

- You are editing a `values.yaml` whose `application.yaml` pins an IDP chart via `chartVersion:` (for example `idp-advanced`, `idp-redis`, `idp-dynamodb`, `idp-oidc-middleware`, …).
- Your editor supports the YAML Language Server. The quickest setup per editor:

  | Editor | Requirement |
  | ------ | ----------- |
  | VS Code | Install the [Red Hat YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) (`redhat.vscode-yaml`). |
  | Neovim | Any LSP client with `yaml-language-server` registered. |
  | JetBrains IDEs | Built-in JSON Schema support — no extension needed. |

## Where the schemas live

Each chart's schema is published at:

```
https://public.docs.idp.jppol.dk/schemas/<chart>/v<version>.json
```

A moving `latest.json` is also published, but for daily work we recommend the pinned `v<version>.json` so a chart release never surprises you mid-edit.

**Example URLs (at the time of writing):**

- `https://public.docs.idp.jppol.dk/schemas/idp-advanced/v3.1.2.json`
- `https://public.docs.idp.jppol.dk/schemas/idp-redis/v0.8.0.json`
- `https://public.docs.idp.jppol.dk/schemas/idp-oidc-middleware/v0.3.0.json`

Match the version in the URL to the `chartVersion:` in your `application.yaml`.

## Option 1: inline modeline (recommended)

Add a single comment on the first line of `values.yaml`. Works in VS Code, Neovim, JetBrains, and anything else that runs the YAML Language Server:

```yaml
# yaml-language-server: $schema=https://public.docs.idp.jppol.dk/schemas/idp-advanced/v3.1.2.json
replicaCount: 1
image:
  repository: 354918371398.dkr.ecr.eu-west-1.amazonaws.com/idp/myapp
  tag: "0.1.0"
# …rest of values.yaml
```

Reload the editor (or close/reopen the file) after adding the line the first time.

**When you bump `chartVersion`**, update the version in the modeline too so your IDE validates against the schema that Helm will actually apply.

## Option 2: VS Code `settings.json` mapping

If you work in a large apps repository and prefer not to add a modeline to each file, configure a glob in your VS Code settings instead (`.vscode/settings.json` in the repo, or user settings):

```json
{
  "yaml.schemas": {
    "https://public.docs.idp.jppol.dk/schemas/idp-advanced/v3.1.2.json": [
      "apps/**/values.yaml"
    ]
  }
}
```

The drawback is that every app under the glob is assumed to use the same chart version. Modelines scale better when apps pin different versions.

## Verify it works

1. Hover over a field you know has a description, for example `ingress.public.enabled`. You should see its description in a tooltip, plus a small attribution line identifying the schema file.
2. Set an invalid enum value to confirm validation fires:

    ```yaml
    compute:
      arch: x86  # invalid — schema only allows amd64 or arm64
    ```

    You should see a red squiggle under `x86` and a matching entry in the **Problems** panel (VS Code: <kbd>Ctrl+Shift+M</kbd>).

3. Press <kbd>Ctrl+Space</kbd> on an empty line inside a nested object (for example inside `compute:`). The suggestions should list only the valid sub-keys from the schema.

## Troubleshooting

**Nothing happens in VS Code.**
Check that `redhat.vscode-yaml` is installed and enabled for the current workspace. Then reload the window (<kbd>Ctrl+Shift+P</kbd> → `Developer: Reload Window`). The schema is fetched once per session and cached — if you edit the modeline URL, reload afterwards.

**Hover only shows the schema attribution, no description.**
The field exists in the schema but has no description yet. That is a gap in the chart's `values.yaml` comments. Report it in Slack and we will fix the chart; a later chart release will republish an enriched schema automatically.

**`HTTP 404` when the IDE fetches the schema.**
The version you pinned in the modeline has not been published. Either it is a chart that does not ship a `values.schema.json`, or the version pre-dates the publishing pipeline (anything before April 2026). Pin to a newer `v<version>.json` from the same chart, or use `latest.json` to be sure.

**Schema updates are not picked up.**
Your IDE caches the schema. Reload the window after changing the modeline URL, or restart the editor.

## Getting help

Ping the IDP team on Slack if a chart you rely on is missing from the schema catalogue, if a schema looks wrong, or if you want us to add description coverage for a specific field.
