# It

This project ships with the [Paddle Billing](https://developer.paddle.com/) agent skills
installed, so any agent-skills-compatible coding tool working in this repo gets step-by-step
guidance for Paddle integration tasks instead of guessing at the API.

## Installed skills

Ten skills live in [`.agents/skills/`](.agents/skills), one directory per skill, each with a
`SKILL.md` containing YAML frontmatter (`name`, `description`) plus the instructions.

| Skill | What it covers |
| --- | --- |
| [`paddle-billing-history`](.agents/skills/paddle-billing-history/SKILL.md) | List transactions for the authenticated customer via the Node SDK: mandatory `customerId` filter, cursor pagination, status filtering, and formatting totals in lowest currency units. |
| [`paddle-catalog-setup`](.agents/skills/paddle-catalog-setup/SKILL.md) | Create the products and prices the other skills depend on — MCP tools first, Node SDK seed script as fallback, dashboard steps as last resort. |
| [`paddle-checkout-web`](.agents/skills/paddle-checkout-web/SKILL.md) | Add an overlay or inline Paddle Checkout to a Next.js app, with event handling, customer pre-fill, and dynamic line items. |
| [`paddle-customer-portal`](.agents/skills/paddle-customer-portal/SKILL.md) | Mint a customer portal session URL from a Server Action — auth, ownership, overview vs deep-link URLs, and the security model. |
| [`paddle-pricing-pages`](.agents/skills/paddle-pricing-pages/SKILL.md) | Render country-localized prices with `Paddle.PricePreview()` — country detection, billing-frequency toggle, currency formatting. |
| [`paddle-sandbox-testing`](.agents/skills/paddle-sandbox-testing/SKILL.md) | Exercise the integration end to end in sandbox: test cards, webhook simulator, local tunnels — no real money. |
| [`paddle-subscription-cancel`](.agents/skills/paddle-subscription-cancel/SKILL.md) | Cancel a subscription from a Server Action — ownership check, safe `effectiveFrom` default, revalidation, `canceled` vs `scheduledChange`. |
| [`paddle-subscription-sync`](.agents/skills/paddle-subscription-sync/SKILL.md) | Mirror Paddle subscription and customer state into your database via webhooks — schema, upsert, status semantics, scheduled changes. |
| [`paddle-subscription-update`](.agents/skills/paddle-subscription-update/SKILL.md) | Change plan via a Server Action — `prorationBillingMode`, items-array replace semantics, preview-before-commit, `on_payment_failure`. |
| [`paddle-webhooks`](.agents/skills/paddle-webhooks/SKILL.md) | Receive and verify webhooks in a Next.js Route Handler — signature verification, idempotency, retry semantics, local testing. |

`.agents/skills/` is the tool-agnostic "universal" location used by the `skills` CLI; tools
with their own directory (`.claude/skills`, `.cursor/skills`, `.codex/skills`, …) can be linked
to it by re-running the install command with `--agent <name>`.

## Reinstalling or adding more

The skills come from Paddle's published skill index. The documented install command is:

```sh
pnpm dlx skills add https://developer.paddle.com/
```

Equivalent install from the official source repository
([`PaddleHQ/paddle-agent-skills`](https://github.com/PaddleHQ/paddle-agent-skills)) — use this
when `developer.paddle.com` is unreachable from your environment:

```sh
pnpm dlx skills add PaddleHQ/paddle-agent-skills --agent amp --skill '*' --yes --copy
```

Useful flags: `-l/--list` to preview available skills, `-s/--skill <name>` to install one,
`--copy` to write real files instead of symlinks (what this repo uses, so the skills commit
cleanly), and `-g/--global` for a user-level install.

## Updating

[`skills-lock.json`](skills-lock.json) records each skill's source, path, and a folder hash, so
updates are reproducible:

```sh
pnpm dlx skills update -p      # project skills
pnpm dlx skills list           # show what's installed
```

These skills target **Paddle Billing**, not the legacy Paddle Classic product — the two have
different APIs, and Classic content does not apply here.

## Source

- Skill index: https://developer.paddle.com/.well-known/skills/index.json
- Docs index for agents: https://developer.paddle.com/llms.txt
- Skills CLI: https://github.com/vercel-labs/skills
- Upstream skills: https://github.com/PaddleHQ/paddle-agent-skills (Apache-2.0)
