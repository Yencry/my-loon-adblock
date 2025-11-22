#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Analyze overlap between different rule sources.

This script reuses parsing logic from generate_rules.py to:

- Fetch each source defined in generate_rules.SOURCES and DIRECT_SOURCES
- Build a domain set per source
- Output statistics about:
  - Per-source totals and unique domains
  - Pairwise intersections ("重复度") between all sources

Usage (from repo root):

    python analyze_rules_overlap.py

Outputs under ./dist/:

- rules_overlap_sources.csv : per-source statistics
- rules_overlap_pairs.csv   : pairwise overlap matrix (long format)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List, Set

try:
    from generate_rules import (
        SOURCES,
        DIRECT_SOURCES,
        fetch_text,
        extract_domains,
    )
except Exception as e:  # pragma: no cover - simple logging
    print(f"[error] failed to import from generate_rules: {e}", file=sys.stderr)
    raise


def build_source_sets() -> Dict[str, Set[str]]:
    """Fetch all sources and return mapping: source_name -> set(domains)."""

    all_sets: Dict[str, Set[str]] = {}

    def handle_group(sources, prefix: str = "") -> None:
        for src in sources:
            name = src.get("name", "(unknown)")
            url = src.get("url")
            if not url:
                continue
            if src.get("skip"):
                # 跳过仓库根目录这类
                print(f"[skip-analyze] {name}: {url}", file=sys.stderr)
                continue

            full_name = f"{prefix}{name}" if prefix else name
            print(f"[fetch-analyze] {full_name}: {url}", file=sys.stderr)

            try:
                text = fetch_text(url)
            except Exception as e:  # pragma: no cover - simple logging
                print(f"[warn] fetch failed for {full_name}: {e}", file=sys.stderr)
                continue

            domains = extract_domains(text)
            print(
                f"[info] {full_name}: extracted {len(domains)} domains",
                file=sys.stderr,
            )
            all_sets[full_name] = set(domains)

    # Ad / privacy / hosts block lists
    handle_group(SOURCES, prefix="block: ")
    # Direct lists
    handle_group(DIRECT_SOURCES, prefix="direct: ")

    return all_sets


def write_per_source_stats(
    dist_dir: Path, source_sets: Dict[str, Set[str]]
) -> None:
    """Write per-source statistics CSV.

    Columns:
    - source
    - type (block/direct)
    - total_domains
    - unique_domains (only appear in this source)
    - overlapped_domains (appear in >= 2 sources)
    - unique_pct
    - overlapped_pct
    """

    # 统计每个域名出现在多少个源里
    domain_counts: Dict[str, int] = {}
    for domains in source_sets.values():
        for d in domains:
            domain_counts[d] = domain_counts.get(d, 0) + 1

    out_path = dist_dir / "rules_overlap_sources.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "source",
                "type",
                "total_domains",
                "unique_domains",
                "overlapped_domains",
                "unique_pct",
                "overlapped_pct",
            ]
        )

        for name, domains in sorted(source_sets.items()):
            total = len(domains)
            if total == 0:
                unique = 0
                overlapped = 0
                unique_pct = 0.0
                overlapped_pct = 0.0
            else:
                unique = sum(1 for d in domains if domain_counts.get(d, 0) == 1)
                overlapped = total - unique
                unique_pct = unique * 100.0 / total
                overlapped_pct = overlapped * 100.0 / total

            if name.startswith("block: "):
                stype = "block"
            elif name.startswith("direct: "):
                stype = "direct"
            else:
                stype = "unknown"

            writer.writerow(
                [
                    name,
                    stype,
                    total,
                    unique,
                    overlapped,
                    f"{unique_pct:.2f}",
                    f"{overlapped_pct:.2f}",
                ]
            )

    print(f"[ok] wrote {out_path}", file=sys.stderr)


def write_pairwise_overlap(
    dist_dir: Path, source_sets: Dict[str, Set[str]]
) -> None:
    """Write pairwise overlap statistics CSV.

    Each row describes one ordered pair (A,B):
    - source_a, source_b
    - size_a, size_b
    - overlap
    - overlap_pct_of_a
    - overlap_pct_of_b
    """

    names: List[str] = sorted(source_sets.keys())
    out_path = dist_dir / "rules_overlap_pairs.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "source_a",
                "source_b",
                "size_a",
                "size_b",
                "overlap",
                "overlap_pct_of_a",
                "overlap_pct_of_b",
            ]
        )

        for i, a in enumerate(names):
            set_a = source_sets[a]
            size_a = len(set_a)
            for j, b in enumerate(names):
                set_b = source_sets[b]
                size_b = len(set_b)
                if size_a == 0 or size_b == 0:
                    overlap = 0
                    pct_a = 0.0
                    pct_b = 0.0
                else:
                    # 对称交集
                    overlap = len(set_a & set_b)
                    pct_a = overlap * 100.0 / size_a
                    pct_b = overlap * 100.0 / size_b

                writer.writerow(
                    [
                        a,
                        b,
                        size_a,
                        size_b,
                        overlap,
                        f"{pct_a:.2f}",
                        f"{pct_b:.2f}",
                    ]
                )

    print(f"[ok] wrote {out_path}", file=sys.stderr)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    dist_dir = base_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    source_sets = build_source_sets()
    if not source_sets:
        print("[error] no sources could be fetched", file=sys.stderr)
        return

    write_per_source_stats(dist_dir, source_sets)
    write_pairwise_overlap(dist_dir, source_sets)


if __name__ == "__main__":
    main()
