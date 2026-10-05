---
name: critic-markup
description: Use CriticMarkup to propose tracked, reviewable edits to prose (Markdown, docs, essays, READMEs) instead of silently overwriting the text. Activate when the user asks for edits, revisions, proofreading, or feedback on writing and wants to see and accept/reject each change.
---

# critic-markup

CriticMarkup is a lightweight syntax for marking up changes to prose, like "track changes" in a word processor but in plain text. Instead of overwriting the user's writing, you wrap each edit in CriticMarkup tags so the author can review, then accept or reject each one.

## When to use

Use this skill when editing **prose** — essays, documentation, READMEs, blog posts, letters, reports, or any natural-language text — and the user wants their original words preserved so they can review your changes. Signals include: "proofread", "edit", "revise", "suggest changes", "mark up", "give feedback", "tighten this", "track changes".

**Do not use** for:
- Source code, config files, or data files (use normal edits — CriticMarkup is not valid syntax there).
- First drafts or net-new content the user asked you to write from scratch.
- Cases where the user explicitly wants you to just rewrite the text cleanly ("just fix it", "rewrite this").

If unsure whether the user wants tracked changes or a clean rewrite, ask.

## Syntax

CriticMarkup defines five markup types. Each must open and close on tags that can span words, sentences, or paragraphs.

| Change | Syntax | Example |
|--------|--------|---------|
| **Addition** | `{++ ... ++}` | `The cat sat{++ quietly++} on the mat.` |
| **Deletion** | `{-- ... --}` | `The cat {--really --}sat on the mat.` |
| **Substitution** | `{~~ old ~> new ~~}` | `The cat {~~sat~>lounged~~} on the mat.` |
| **Comment** | `{>> ... <<}` | `The cat sat.{>> Consider naming the cat here. <<}` |
| **Highlight** | `{== ... ==}{>> ... <<}` | `{==The cat sat on the mat.==}{>> This sentence is passive. <<}` |

Notes:
- **Substitution** is preferred over a separate delete + add when you are replacing text in place — it reads more clearly as "change X to Y".
- **Comments** (`{>> <<}`) carry editorial notes that are not themselves edits. Use them to explain *why* you made a change or to flag something for the author's judgment.
- **Highlight** is a comment anchored to a specific span; always pair `{== ==}` with a following `{>> <<}`.
- Whitespace inside the tags is part of the change. Mind surrounding spaces so the accepted text reads correctly — e.g. put the space inside the addition (`sat{++ quietly++}`) rather than leaving a double space.
- **Avoid hard line breaks inside a single markup tag.** A tag that straddles a newline is harder to read and some tooling parses it poorly. Keep each `{++ ++}` / `{-- --}` / `{~~ ~> ~~}` / `{>> <<}` on one line.

### Unfill before marking up

The author uses Emacs column filling (`fill-paragraph`), so paragraphs arrive hard-wrapped at a fixed column. Those hard line breaks collide with the "no line breaks inside a tag" rule above. Before adding CriticMarkup:

1. **Un-fill the entire affected paragraph** — join its wrapped lines into one long line (replace each intra-paragraph newline with a single space), so the paragraph is a single logical line. Un-fill the *whole* paragraph, not just the span you're editing, so filled and unfilled lines aren't mixed within one paragraph.
2. Then insert your markup into that unfilled paragraph.

This keeps every tag on a single line and leaves the author free to re-fill (`fill-paragraph` / `M-q`) once they've accepted or rejected the changes. Do not re-fill the paragraph yourself — leave it unfilled so the markup stays intact for review.

## Instructions

1. **Confirm the target is prose** and that tracked changes (not a clean rewrite) are wanted. Read the file first.
2. **Un-fill any paragraph you're about to edit** (join its hard-wrapped lines into one line) so no markup tag ends up straddling a line break — see "Unfill before marking up" above.
3. **Make each change with CriticMarkup tags**, leaving all original text intact inside `{-- --}` / `{~~ ~~}` rather than deleting it outright. Edit the file in place using these tags.
4. **Prefer the most specific markup**: substitution for replacements, deletion for cuts, addition for inserts. Keep each markup span tight — mark the smallest text that captures the change, not the whole surrounding sentence.
5. **Explain non-obvious edits** with an inline comment `{>> ... <<}` so the author understands your reasoning. Don't comment on trivial fixes (typos, obvious grammar).
6. **Do not nest** CriticMarkup tags inside each other. For a complex rewrite of one passage, use a single substitution.
7. **Preserve the author's voice.** Suggest, don't impose. When a change is a matter of taste rather than correctness, prefer a highlight + comment over a forced edit.
8. **Lint before handing back**: run `python3 scripts/criticmarkup.py check FILE` and fix anything it flags (tags spanning line breaks, unbalanced delimiters) — see "Linting your markup" below.
9. **Summarize** after editing: briefly list the kinds of changes you made (e.g. "3 grammar fixes, 2 wording suggestions, 1 flagged passage") so the author knows what to review.

## Accepting and rejecting changes

CriticMarkup is resolved by applying each markup:
- **Accept** an addition/substitution → keep the new text; a deletion → remove the text; drop all comment/highlight tags.
- **Reject** → keep the original text; drop the markup.

Resolving every tag by hand is error-prone, so use the bundled script for whole-file operations:

```sh
python3 scripts/criticmarkup.py resolve --accept -i FILE   # accept all, rewrite in place
python3 scripts/criticmarkup.py resolve --reject -i FILE   # reject all, rewrite in place
python3 scripts/criticmarkup.py resolve --accept FILE      # or print to stdout
```

When the user asks to "accept all changes" / "finalize", run `resolve --accept`; for "reject all", run `resolve --reject`. The script applies every markup deterministically (additions/substitutions/highlights kept or discarded per direction; comments always dropped) and leaves clean prose. The user may also accept/reject *individual* changes with an editor extension (the CriticMarkup plugins for VS Code, Sublime Text, or Obsidian) — leave the markup in place for that.

## Linting your markup

After editing, verify your markup is well-formed with the same script:

```sh
python3 scripts/criticmarkup.py check FILE
```

It exits non-zero and prints a line-numbered report if any tag spans a line break (the "un-fill first" rule above) or if a delimiter is unbalanced/malformed. Run it on files you've marked up before handing them back, and fix anything it flags.
