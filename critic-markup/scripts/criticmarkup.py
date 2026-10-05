#!/usr/bin/env python3
"""Deterministic CriticMarkup resolver and linter.

Two jobs an LLM should not do by hand:

  resolve  Accept or reject *all* markup, producing clean prose. Mechanical and
           must be exact, so do it with regex, not by eyeballing tags.
  check    Lint markup for the mistakes this skill warns about: a tag that
           spans a newline (breaks the "one tag per line" rule), or an
           unbalanced / malformed tag.

Stdlib only; Python 3.8+. Inspired by pancritic
(https://github.com/ickc/pancritic), trimmed to the accept/reject core.

CriticMarkup syntax:
    addition      {++ ... ++}
    deletion      {-- ... --}
    substitution  {~~ old ~> new ~~}
    comment       {>> ... <<}
    highlight     {== ... ==}

Usage:
    criticmarkup.py resolve --accept [FILE]     # FILE or stdin -> stdout
    criticmarkup.py resolve --reject [FILE]
    criticmarkup.py resolve --accept -i FILE     # rewrite FILE in place
    criticmarkup.py check [FILE]                 # exit 1 if issues found
"""
from __future__ import annotations

import argparse
import re
import sys

# Canonical CriticMarkup patterns. DOTALL so a (malformed) span can match
# across newlines — the linter relies on that to flag such spans.
ADD = re.compile(r"\{\+\+(?P<value>.*?)\+\+\}", re.DOTALL)
DEL = re.compile(r"\{--(?P<value>.*?)--\}", re.DOTALL)
SUB = re.compile(r"\{~~(?P<old>.*?)~>(?P<new>.*?)~~\}", re.DOTALL)
COMMENT = re.compile(r"\{>>(?P<value>.*?)<<\}", re.DOTALL)
HIGHLIGHT = re.compile(r"\{==(?P<value>.*?)==\}", re.DOTALL)

# Bare delimiters, used to detect unbalanced markup after well-formed tags
# have been stripped.
DELIMITERS = ["{++", "++}", "{--", "--}", "{~~", "~>", "~~}", "{>>", "<<}", "{==", "==}"]


def resolve(text: str, accept: bool) -> str:
    """Apply every markup in the accept or reject direction."""
    # Substitutions first: their inner `~>` must not be seen by add/del passes.
    text = SUB.sub(lambda m: m.group("new") if accept else m.group("old"), text)
    text = ADD.sub(lambda m: m.group("value") if accept else "", text)
    text = DEL.sub(lambda m: "" if accept else m.group("value"), text)
    # Comments and highlights are never part of the finalized prose.
    text = COMMENT.sub("", text)
    text = HIGHLIGHT.sub(lambda m: m.group("value"), text)
    return text


def _lineno(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def check(text: str) -> list[str]:
    """Return a list of human-readable lint issues (empty == clean)."""
    issues: list[str] = []
    named = [
        ("addition", ADD),
        ("deletion", DEL),
        ("substitution", SUB),
        ("comment", COMMENT),
        ("highlight", HIGHLIGHT),
    ]
    for name, pattern in named:
        for m in pattern.finditer(text):
            if "\n" in m.group(0):
                issues.append(
                    f"line {_lineno(text, m.start())}: {name} tag spans a line "
                    f"break; un-fill the paragraph so the tag stays on one line"
                )
    # Strip well-formed tags, then any surviving delimiter is unbalanced.
    stripped = text
    for pattern in (SUB, ADD, DEL, COMMENT, HIGHLIGHT):
        stripped = pattern.sub("", stripped)
    for token in DELIMITERS:
        idx = stripped.find(token)
        if idx != -1:
            issues.append(
                f"line {_lineno(stripped, idx)}: stray '{token}' — "
                f"unbalanced or malformed markup"
            )
    return issues


def _read(path: str | None) -> str:
    if path in (None, "-"):
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_resolve = sub.add_parser("resolve", help="accept or reject all markup")
    direction = p_resolve.add_mutually_exclusive_group(required=True)
    direction.add_argument("--accept", action="store_true", help="keep every proposed change")
    direction.add_argument("--reject", action="store_true", help="discard every proposed change")
    p_resolve.add_argument("file", nargs="?", help="input file (default: stdin)")
    p_resolve.add_argument("-i", "--in-place", action="store_true", help="rewrite FILE in place")

    p_check = sub.add_parser("check", help="lint markup; exit 1 if issues found")
    p_check.add_argument("file", nargs="?", help="input file (default: stdin)")

    args = parser.parse_args(argv)

    if args.command == "resolve":
        text = _read(args.file)
        out = resolve(text, accept=args.accept)
        if args.in_place:
            if not args.file or args.file == "-":
                parser.error("--in-place requires a FILE")
            with open(args.file, "w", encoding="utf-8") as fh:
                fh.write(out)
        else:
            sys.stdout.write(out)
        return 0

    # check
    text = _read(args.file)
    issues = check(text)
    for issue in issues:
        print(issue, file=sys.stderr)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
