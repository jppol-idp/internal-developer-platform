# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll-based documentation site for an Internal Developer Platform (IDP) team, hosted on GitHub Pages. The site uses the "Just the Docs" theme and serves both internal (IDP team only) and public documentation.

- **Internal docs**: https://docs.idp.jppol.dk
- **Public docs**: https://jppol-idp.github.io/internal-developer-platform/
- **Repository**: https://github.com/jppol-idp/docs

## Site Structure

The site is organized into major sections:
- `/how-to/` - How-to guides (mostly public)
- `/architecture-decision-records/` - ADRs for technology and architectural decisions
- `/dokumentation/` - General documentation
- `/onboarding/` - Onboarding content
- `/referater/` - Meeting minutes
- `/baggrund/` - Background/context documents
- `/ecosystem/` - Information about related systems
- `/_includes/` - Jekyll include templates

The site uses YAML frontmatter with these key fields:
- `title` - Document title (used for navigation and sorting)
- `nav_order` - Navigation order (numeric)
- `parent` - Parent section in navigation
- `domain` - Either `public` or `private` (controls visibility)
- `permalink` - URL path override
- `last_reviewed_on` - Last review date (YYYY-MM-DD)
- `review_in` - Review cadence (e.g., "6 months")

## Building and Serving

The site is built with Jekyll and requires Ruby. Common commands:

```bash
# Install dependencies
bundle install

# Serve locally (development)
bundle exec jekyll serve

# Build static site
bundle exec jekyll build

# Build for public site (excludes private content)
bundle exec jekyll build --config _config.public.yml
```

The site will be available at `http://localhost:4000` during local development.

## Navigation Ordering

The `nav_order` field controls document ordering within sections. Use the provided script to automatically assign nav_order values alphabetically by title:

```bash
# Dry run (shows what would change)
./scripts/sort-nav-order.sh --dry-run <directory>

# Apply changes
./scripts/sort-nav-order.sh <directory>
```

The script handles macOS (with `-i ''`) and Linux (with `-i`) sed syntax differences automatically.

## Important Notes

- **Language**: Documentation is primarily in Danish with some English
- **Public vs Private**: The `domain` field determines visibility. Use `domain: public` for public docs and `domain: private` for internal-only content
- **Architecture Decision Records**: Stored in `/architecture-decision-records/` with a specific format including Status, Context, Decision, and Consequences sections
- **Configuration**: Main config is `_config.yml` (includes private content) and `_config.public.yml` (excludes private content)
- **GitHub Pages**: Builds automatically from the `main` branch when pushed to GitHub
- **Theme**: Uses "Just the Docs" theme (remote_theme: just-the-docs/just-the-docs)

## Redis Documentation (`how-to/redis.md`)

This is a key how-to guide documenting the IDP Redis Helm chart deployment. When updating this document:

- **Source of truth**: `/how-to/redis.md` reflects the current state of the `helm-idp-redis` chart (https://github.com/jppol-idp/helm-idp-redis)
- **Key sections**:
  - Deployment modes (standalone vs replication with Sentinel)
  - Resource management and QoS classes (critical for production)
  - Configuration examples for development and production
  - Service discovery and access patterns
  - Authentication and monitoring setup

- **Important to maintain**: When the helm chart changes (especially `values-simple.yaml`), update the documentation examples to match. This includes resource requests/limits, persistence settings, and replica counts.

- **QoS guidance**: The document includes production recommendations for Guaranteed QoS (request == limit) to prevent pod evictions.

## ECR Pull-Through Cache Documentation

This is a how-to guide documenting the Docker Hub image caching solution via AWS ECR. When updating this documentation:

- **Source of truth**: `/how-to/docker-hub-image-caching.md` documents the ECR pull-through cache implementation
- **Internal details**: `/dokumentation/ecr-pull-through-cache.md` contains technical implementation details for the team
- **Key implementation details**:
  - Developers explicitly update Docker Hub image references to ECR cache URLs
  - Official Docker Hub images require the `/library/` prefix (e.g., `nginx:latest` → `.../docker-hub/library/nginx:latest`)
  - Organization/user images do not use the `/library/` prefix (e.g., `grafana/grafana:latest` → `.../docker-hub/grafana/grafana:latest`)
  - ECR account: 354918371398, region: eu-west-1

- **Future expansion path**: The infrastructure supports adding additional registry caches (ghcr.io, quay.io, etc.) in the future without architectural changes. Each registry would use a new cache prefix pattern.

## Recent Changes Pattern

Recent commits show the team frequently updates nav_order values and adds content to how-to guides. When adding new documents, ensure proper frontmatter including nav_order and domain fields.

## Writing customer-facing how-to guides

When adding or significantly editing a how-to in `/how-to/`, treat it as a product the customer reads cold. They have not seen the conversation that produced it, they do not know the IDP team's internal naming, and they cannot ask follow-up questions before they get stuck.

### End-to-end customer-perspective review (mandatory before merging)

After writing a how-to, **always do a final pass reading the document from start to finish as if you were a new customer encountering it for the first time**. Do not skip this. Reviewing in fragments while writing is not the same — bugs hide in the seams between sections. Look specifically for:

1. **Placeholder consistency.** Pick one convention for example values (`my-namespace`, `myapp`, etc.) and use it everywhere in code blocks. Mixing `<your-namespace>` with `my-namespace` looks sloppy and makes new readers wonder if `my-namespace` is literal.
2. **Unintroduced acronyms.** Expand every acronym on first use, even ones the team uses daily (ESO → External Secrets Operator). Customers do not live in our jargon.
3. **Forward references that work standalone.** When you say "see step 2", verify step 2 actually contains what you promised. When troubleshooting suggests a fix, make sure that fix is reachable without scrolling through unrelated sections.
4. **Tautological tables and lists.** Cut anything that restates information the reader already has. If a customer asked for a display name, they do not need to "extract" the display name from the response.
5. **Bridge between abstract examples and real screenshots.** If a screenshot shows a real deployment with concrete names (e.g. `idp-alert-overview-oidc`) but the rest of the doc uses placeholders (`myapp-oidc`), explicitly explain the relationship in one sentence so the reader does not think they are looking at a different system.
6. **Casing/naming variants.** If you use `MyApp` for human-readable names and `myapp` for slugs, call it out once so the reader knows which one to put where.
7. **Pinned versions in examples.** Always add a comment in the YAML noting the example version is illustrative, plus a link to where the latest version can be found.

### Customer language conventions

- **No "Traefik".** Customers do not know they use Traefik — they configure ingress via `ingress.public.enabled` / `ingress.private.enabled` in idp-advanced. Use "ingress middleware" or "OIDC middleware" instead. The technical chart README can mention Traefik freely; public docs should not.
- **"servicedesk" is one word.** Never "service desk".
- **Support sections direct customers to the IDP team on Slack**, not to "idp-support" or "platform engineers".
- **Things outside the IDP team's area** (e.g. Entra app management, AD groups) should be explicitly attributed to servicedesk or the relevant external team — do not make claims about how they will be delivered or what the customer can self-serve.
- **Do not recommend third-party websites for generating secrets**, even client-side ones. Show local one-liners (Python, Node, Bash, browser DevTools console) instead.
