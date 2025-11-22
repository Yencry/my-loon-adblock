#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plot charts for rules overlap analysis.

This script reads the CSV files produced by analyze_rules_overlap.py and
creates simple visualization charts:

- Per-source stacked bar chart: unique vs overlapped percentage
- Pairwise overlap heatmap: overlap_pct_of_a matrix

Usage (from repo root):

    python plot_rules_overlap.py

Optional:

    python plot_rules_overlap.py --dist ./dist

Outputs (under dist/ by default):

- rules_overlap_sources_bar.png
- rules_overlap_pairs_heatmap.png
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Dict

try:  # lazy import with friendly error
    import matplotlib.pyplot as plt
    from matplotlib import rcParams
except ImportError as e:  # pragma: no cover - simple logging
    print(
        "[error] matplotlib is required for plotting. Install it with:\n"
        "    pip install matplotlib\n",
        file=sys.stderr,
    )
    raise

# Configure a Chinese-capable font (Windows: Microsoft YaHei / SimHei)
rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "sans-serif"]
rcParams["axes.unicode_minus"] = False


def load_sources_csv(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"sources CSV not found: {path}")
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def load_pairs_csv(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"pairs CSV not found: {path}")
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def shorten_name(name: str) -> str:
    """Shorten long source names a bit for plotting labels."""

    # strip common prefixes
    for prefix in ("block: ", "direct: "):
        if name.startswith(prefix):
            name = name[len(prefix) :]
            break
    return name


def plot_sources_bar(rows: List[Dict[str, str]], out_path: Path) -> None:
    if not rows:
        print("[warn] no rows for sources bar chart", file=sys.stderr)
        return

    names = [shorten_name(r["source"]) for r in rows]
    unique_pct = [float(r.get("unique_pct", 0.0)) for r in rows]
    overlapped_pct = [float(r.get("overlapped_pct", 0.0)) for r in rows]

    x = list(range(len(names)))

    plt.figure(figsize=(max(8, len(names) * 0.5), 6))
    plt.bar(x, unique_pct, label="唯一域名占比")
    plt.bar(x, overlapped_pct, bottom=unique_pct, label="与其他源重叠占比")

    plt.xticks(x, names, rotation=60, ha="right", fontsize=8)
    plt.ylabel("域名百分比 (%)")
    plt.title("各规则源唯一 / 重叠域名占比")
    plt.legend()
    plt.tight_layout()

    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[ok] wrote {out_path}", file=sys.stderr)


def plot_pairs_heatmap(rows: List[Dict[str, str]], out_path: Path) -> None:
    if not rows:
        print("[warn] no rows for pairs heatmap", file=sys.stderr)
        return

    # collect names from CSV
    names_set = set()
    for r in rows:
        names_set.add(r["source_a"])
        names_set.add(r["source_b"])
    names = sorted(names_set)
    name_to_idx = {n: i for i, n in enumerate(names)}

    n = len(names)
    # initialize matrix with zeros
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]

    for r in rows:
        a = r["source_a"]
        b = r["source_b"]
        i = name_to_idx[a]
        j = name_to_idx[b]
        try:
            pct = float(r.get("overlap_pct_of_a", 0.0))
        except ValueError:
            pct = 0.0
        matrix[i][j] = pct

    short_names = [shorten_name(n) for n in names]

    plt.figure(figsize=(max(8, n * 0.5), max(6, n * 0.5)))
    im = plt.imshow(matrix, cmap="viridis", aspect="auto", origin="upper")
    plt.colorbar(im, label="A 源的重叠百分比")

    plt.xticks(range(n), short_names, rotation=60, ha="right", fontsize=8)
    plt.yticks(range(n), short_names, fontsize=8)

    plt.xlabel("规则源 B")
    plt.ylabel("规则源 A")
    plt.title("规则源两两重叠情况（相对于 A 的百分比）")
    plt.tight_layout()

    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[ok] wrote {out_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot charts for rules overlap analysis (requires matplotlib)."
    )
    parser.add_argument(
        "--dist",
        default="dist",
        help="Directory where CSV files are located and images will be written (default: dist)",
    )
    args = parser.parse_args()

    dist_dir = Path(args.dist).resolve()
    dist_dir.mkdir(parents=True, exist_ok=True)

    sources_csv = dist_dir / "rules_overlap_sources.csv"
    pairs_csv = dist_dir / "rules_overlap_pairs.csv"

    try:
        sources_rows = load_sources_csv(sources_csv)
    except FileNotFoundError as e:
        print(f"[error] {e}", file=sys.stderr)
        sources_rows = []

    try:
        pairs_rows = load_pairs_csv(pairs_csv)
    except FileNotFoundError as e:
        print(f"[error] {e}", file=sys.stderr)
        pairs_rows = []

    if not sources_rows and not pairs_rows:
        print("[error] no CSV data available; run analyze_rules_overlap.py first", file=sys.stderr)
        return

    if sources_rows:
        bar_path = dist_dir / "rules_overlap_sources_bar.png"
        plot_sources_bar(sources_rows, bar_path)

    if pairs_rows:
        heatmap_path = dist_dir / "rules_overlap_pairs_heatmap.png"
        plot_pairs_heatmap(pairs_rows, heatmap_path)


if __name__ == "__main__":
    main()
