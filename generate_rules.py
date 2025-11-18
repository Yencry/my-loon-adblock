#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Aggregate multiple ad / privacy / hosts rules into a single domain set.

Outputs (under ./dist):
- aggregate-domains.txt      : one domain per line
- clash-domain-rules.yaml    : Clash rule-provider (behavior: domain)
- loon-domain-rules.conf     : Loon remote rule file (DOMAIN-SUFFIX,domain)

You can reference the same domain set in Clash / Loon with different
policies (分流 / 拒绝 / 直连) on the client side.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable, Set
from urllib.request import Request, urlopen

# 当前聚合的规则源（来自 index.html 表格）
SOURCES = [
    {
        "name": "anti-AD (AdGuard)",
        "url": "https://anti-ad.net/adguard.txt",
    },
    {
        "name": "Loyalsoldier clash-rules (repo root, skipped)",
        "url": "https://github.com/Loyalsoldier/clash-rules",
        "skip": True,  # 仓库地址本身不是规则文件，暂时跳过
    },
    {
        "name": "Adblock Warning Removal List",
        "url": "https://easylist-downloads.adblockplus.org/antiadblockfilters.txt",
    },
    {
        "name": "AdGuard DNS filter",
        "url": "https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt",
    },
    {
        "name": "EasyList",
        "url": "https://easylist-downloads.adblockplus.org/easylist.txt",
    },
    {
        "name": "EasyList China",
        "url": "https://easylist-downloads.adblockplus.org/easylistchina.txt",
    },
    {
        "name": "EasyPrivacy",
        "url": "https://easylist-downloads.adblockplus.org/easyprivacy.txt",
    },
    {
        "name": "Fanboy Annoyance List",
        "url": "https://easylist-downloads.adblockplus.org/fanboy-annoyance.txt",
    },
    {
        "name": "Fanboy Social Blocking List",
        "url": "https://easylist-downloads.adblockplus.org/fanboy-social.txt",
    },
    {
        "name": "HaGeZi Light (adblock)",
        "url": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/light.txt",
    },
    {
        "name": "hBlock hosts_adblock",
        "url": "https://hblock.molinero.dev/hosts_adblock.txt",
    },
    {
        "name": "StevenBlack Unified hosts",
        "url": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    },
]

# 粗略匹配域名的正则（不含 IP）
DOMAIN_PATTERN = re.compile(
    r"(?<![0-9A-Za-z._-])([A-Za-z0-9][A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![0-9A-Za-z._-])"
)
IP_PATTERN = re.compile(r"^\d{1,3}(?:\.\d{1,3}){3}$")


def fetch_text(url: str, timeout: int = 30) -> str:
    headers = {"User-Agent": "my-dns-ruleboard/1.0"}
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:  # nosec - user runs locally
        data = resp.read()
        # 尝试从 header 拿编码，失败则退回 utf-8
        charset = resp.headers.get_content_charset() or "utf-8"
        try:
            return data.decode(charset, errors="ignore")
        except LookupError:
            return data.decode("utf-8", errors="ignore")


def clean_domain(raw: str) -> str | None:
    d = raw.strip().lstrip(".").lower()
    if not d:
        return None
    if IP_PATTERN.match(d):
        return None
    if d in {"localhost"}:
        return None
    # 过滤掉明显非法的
    if ".." in d:
        return None
    return d


def iter_domains_from_line(line: str) -> Iterable[str]:
    s = line.strip()
    if not s:
        return

    # 注释行
    if s.startswith(("#", "//", "!", ";", "[")):
        return

    # Adblock 白名单，忽略
    if s.startswith("@@"):
        return

    # hosts 格式：0.0.0.0 example.com / 127.0.0.1 example.com
    m = re.match(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([A-Za-z0-9.-]+)", s)
    if m:
        d = clean_domain(m.group(1))
        if d:
            yield d
        return

    # Adblock: ||example.com^ 或 |https://example.com^ 之类
    m = re.search(r"\|\|([A-Za-z0-9.-]+\.[A-Za-z]{2,})\^", s)
    if m:
        d = clean_domain(m.group(1))
        if d:
            yield d
        return

    # AdGuard / Loon / Surge 类似：DOMAIN-SUFFIX,example.com / DOMAIN,example.com
    if s.upper().startswith(("DOMAIN-SUFFIX,", "DOMAIN,")):
        parts = s.split(",", 2)
        if len(parts) >= 2:
            d = clean_domain(parts[1])
            if d:
                yield d
        return

    # Fallback：在整行里查找看起来像域名的片段
    for cand in DOMAIN_PATTERN.findall(s):
        d = clean_domain(cand)
        if d:
            yield d


def extract_domains(text: str) -> Set[str]:
    out: Set[str] = set()
    for line in text.splitlines():
        for d in iter_domains_from_line(line):
            out.add(d)
    return out


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    dist_dir = base_dir / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    all_domains: Set[str] = set()

    for src in SOURCES:
        name = src.get("name", "(unknown)")
        url = src["url"]
        if src.get("skip"):
            print(f"[skip] {name}: {url}", file=sys.stderr)
            continue
        print(f"[fetch] {name}: {url}", file=sys.stderr)
        try:
            text = fetch_text(url)
        except Exception as e:  # pragma: no cover - simple logging
            print(f"[warn] fetch failed for {name}: {e}", file=sys.stderr)
            continue

        domains = extract_domains(text)
        print(f"[info] {name}: extracted {len(domains)} domains", file=sys.stderr)
        all_domains.update(domains)

    if not all_domains:
        print("[error] no domains extracted", file=sys.stderr)
        return

    sorted_domains = sorted(all_domains)

    # 1) 纯域名列表
    txt_path = dist_dir / "aggregate-domains.txt"
    with txt_path.open("w", encoding="utf-8") as f:
        for d in sorted_domains:
            f.write(d + "\n")
    print(f"[ok] wrote {txt_path}", file=sys.stderr)

    # 2) Clash rule-provider：behavior: domain
    clash_path = dist_dir / "clash-domain-rules.yaml"
    with clash_path.open("w", encoding="utf-8") as f:
        f.write("# Generated by generate_rules.py from my-dns-ruleboard sources\n")
        f.write("# behavior: domain\n")
        f.write("payload:\n")
        for d in sorted_domains:
            f.write(f"  - '+.{d}'\n")
    print(f"[ok] wrote {clash_path}", file=sys.stderr)

    # 3) Loon 远程规则文件：在 Loon 中通过 [Remote Rule] 设置 policy 为 Proxy/REJECT/DIRECT
    loon_path = dist_dir / "loon-domain-rules.conf"
    with loon_path.open("w", encoding="utf-8") as f:
        f.write("# Generated by generate_rules.py from my-dns-ruleboard sources\n")
        for d in sorted_domains:
            f.write(f"DOMAIN-SUFFIX,{d}\n")
    print(f"[ok] wrote {loon_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
