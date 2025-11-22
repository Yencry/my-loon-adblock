#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Extract public-safe Clash rules from a full config.

Usage (from repo root):

    python extract_clash_rules.py path/to/config.yaml

Outputs (next to input file by default):
    <name>.public.yaml : original config minus sensitive sections
    <name>.rules.yaml  : only the `rules:` block

This script is text-based, does not require PyYAML.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple


# Top-level keys to remove completely for the public version
SENSITIVE_TOP_LEVEL_KEYS = {
    "proxies",
    "proxy-providers",
    "proxy-providers-legacy",  # just in case
    "proxy-providers-legacy2",
    "proxy-provider",
    "proxy",
    "secret",
    "external-controller",
}


def get_top_level_key_name(line: str) -> Optional[str]:
    """Return the top-level key name if this line starts a top-level mapping key.

    Very simple heuristic:
    - no leading spaces
    - not a comment
    - contains ':'
    - key part is non-empty
    """

    if not line.strip():
        return None

    if line.startswith(" ") or line.startswith("\t"):
        return None

    stripped = line.lstrip()
    if stripped.startswith("#"):
        return None

    if ":" not in line:
        return None

    key_part = line.split(":", 1)[0].strip()
    if not key_part:
        return None

    return key_part


def split_top_level_blocks(lines: List[str]) -> List[Tuple[Optional[str], List[str]]]:
    """Split file into (key, lines) blocks at top-level mapping keys.

    key == None means "preamble" before the first top-level key.
    """

    blocks: List[Tuple[Optional[str], List[str]]] = []
    current_key: Optional[str] = None
    current_lines: List[str] = []

    for line in lines:
        key = get_top_level_key_name(line)
        if key is not None:
            # new block starts
            if current_lines:
                blocks.append((current_key, current_lines))
            current_key = key
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        blocks.append((current_key, current_lines))

    return blocks


def build_public_from_blocks(
    blocks: List[Tuple[Optional[str], List[str]]]
) -> List[str]:
    """Build a public-safe config by dropping sensitive top-level keys."""

    out: List[str] = []
    for key, blines in blocks:
        if key is None:
            # preamble
            out.extend(blines)
            continue

        if key in SENSITIVE_TOP_LEVEL_KEYS:
            # drop whole block
            continue

        out.extend(blines)

    return out


def build_rules_only_from_blocks(
    blocks: List[Tuple[Optional[str], List[str]]]
) -> List[str]:
    """Return only the `rules:` block (if present)."""

    for key, blines in blocks:
        if key == "rules":
            # ensure file ends with newline
            if not blines[-1].endswith("\n"):
                blines[-1] = blines[-1] + "\n"
            return blines
    return []


def process_file(src: Path, output_dir: Optional[Path] = None) -> None:
    if not src.is_file():
        print(f"[error] input not found: {src}", file=sys.stderr)
        return

    text = src.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    blocks = split_top_level_blocks(lines)

    # Decide output locations
    out_dir = output_dir or src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    public_path = out_dir / f"{src.stem}.public{src.suffix}"
    rules_path = out_dir / f"{src.stem}.rules{src.suffix}"

    # 1) public config
    public_lines = build_public_from_blocks(blocks)
    if public_lines:
        public_text = "".join(public_lines)
        public_path.write_text(public_text, encoding="utf-8")
        print(f"[ok] wrote public config: {public_path}", file=sys.stderr)
    else:
        print("[warn] public output is empty; nothing written", file=sys.stderr)

    # 2) rules-only config
    rules_lines = build_rules_only_from_blocks(blocks)
    if rules_lines:
        rules_text = "".join(rules_lines)
        rules_path.write_text(rules_text, encoding="utf-8")
        print(f"[ok] wrote rules-only config: {rules_path}", file=sys.stderr)
    else:
        print("[warn] no `rules:` block found; rules-only file not written", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract public-safe Clash rules from a full config (no PyYAML required)."
    )
    parser.add_argument(
        "input",
        help="Path to Clash YAML config (e.g. 19aa57285c3.yaml)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Output directory (default: same as input)",
    )

    args = parser.parse_args()

    src = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else None

    process_file(src, out_dir)


if __name__ == "__main__":
    main()
