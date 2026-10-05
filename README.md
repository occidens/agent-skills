# agent-skills

A collection of [agent skills](https://docs.claude.com/en/docs/claude-code/skills) — self-contained instructions (and sometimes scripts) that teach a coding agent how to perform a specific task well.

Each skill lives in its own top-level directory with a `SKILL.md` describing when and how to use it.

## Skills

| Skill | What it does |
|-------|--------------|
| [critic-markup](critic-markup/) | Propose tracked, reviewable edits to prose using [CriticMarkup](http://criticmarkup.com/) instead of silently overwriting the text. Bundles a deterministic resolver/linter. |

## Installing

These skills are structured for installation with the [`skills` CLI](https://www.npmjs.com/package/skills):

```sh
# Install every skill in this repo
npx skills add occidens/agent-skills

# Or install a single skill
npx skills add occidens/agent-skills/critic-markup
```

> Confirm the current CLI flags against the `skills` docs — the ecosystem moves quickly.

To install manually, copy a skill directory into your skills path:

```sh
# Project-scoped (shared with your repo)
cp -r critic-markup /path/to/project/.claude/skills/

# User-scoped (available everywhere)
cp -r critic-markup ~/.claude/skills/
```

The agent will then surface the skill when a task matches its description.

## Prerequisites

- **critic-markup** uses a bundled helper script and expects `python3` (3.8+) on your `PATH`. No third-party packages are required.

## Repository layout

```
agent-skills/
├── README.md
└── <skill-name>/
    ├── SKILL.md          # frontmatter (name, description) + instructions
    └── scripts/          # optional helper scripts the skill invokes
```

## Contributing a skill

1. Create a directory named after the skill (kebab-case).
2. Add a `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: my-skill
   description: One or two sentences. Lead with the trigger — when the agent should reach for this skill.
   ---
   ```
3. Keep the body task-focused: *when to use*, *when not to*, and concrete steps.
4. Put any helper scripts in `scripts/`, keep them dependency-light, and reference them from `SKILL.md` with their path relative to the skill directory.
5. Add a row to the **Skills** table above.
