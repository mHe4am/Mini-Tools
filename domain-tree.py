#!/usr/bin/env python3
"""
domain_tree.py - Group a flat domain/subdomain list into a tab-indented tree.
Useful for MindMapping (XMind)

Usage:
    python3 domain_tree.py domains.txt > tree.txt
    cat domains.txt | python3 domain_tree.py > tree.txt
    python3 domain_tree.py -b 20 domains.txt > tree.txt   # batch large groups
"""
import sys
import argparse
from collections import defaultdict
from urllib.parse import urlparse

# Common multi-label public suffixes (2nd-level ccTLDs).
# Extend this if your targets use other ccTLD patterns not listed here.
MULTI_LABEL_SUFFIXES = {
    "co.uk", "org.uk", "gov.uk", "ac.uk", "net.uk", "sch.uk",
    "co.jp", "ne.jp", "or.jp", "ac.jp", "go.jp",
    "co.kr", "or.kr", "ne.kr",
    "com.au", "net.au", "org.au", "gov.au", "edu.au",
    "co.nz", "org.nz", "govt.nz",
    "com.br", "net.br", "org.br", "gov.br",
    "com.cn", "net.cn", "org.cn", "gov.cn",
    "com.eg", "gov.eg", "edu.eg", "net.eg", "org.eg",
    "com.tr", "gov.tr", "org.tr",
    "co.in", "net.in", "org.in", "gov.in", "co.za",
    "com.mx", "com.sg", "com.hk", "co.il", "com.tw",
}


def normalize(line: str) -> str:
    """Strip scheme/path/port/wildcard, return bare lowercase hostname."""
    s = line.strip().lower()
    if not s:
        return ""
    if "://" in s:
        s = urlparse(s).netloc or s
    s = s.split("/")[0]        # drop any leftover path
    s = s.split(":")[0]        # drop port
    s = s.lstrip("*.")         # drop wildcard prefix
    return s.strip(".")


def registrable_domain(fqdn: str) -> str:
    """Return the apex/registrable domain used for grouping."""
    labels = fqdn.split(".")
    if len(labels) < 2:
        return fqdn
    last_two = ".".join(labels[-2:])
    if len(labels) >= 3 and last_two in MULTI_LABEL_SUFFIXES:
        return ".".join(labels[-3:])
    return last_two


def sort_key(fqdn: str):
    # Reversed labels -> groups parents before children, siblings alphabetically.
    return tuple(fqdn.split(".")[::-1])


def main():
    parser = argparse.ArgumentParser(description="Group a flat domain list into a tab-indented tree.")
    parser.add_argument("input", nargs="?", help="input file (defaults to stdin)")
    parser.add_argument("-n", "--newlines", type=int, default=0,
                         help="blank lines to insert between each output line (default: 0)")
    parser.add_argument("-m", "--markdown", action="store_true",
                         help="output as nested '-' bullet markdown (for pasting into XMind/mind-map tools)")
    parser.add_argument("-b", "--batch-size", type=int, default=0, metavar="N",
                         help="group subdomains of large domains under 'Batch NN' nodes, N per batch "
                              "(applies to domains with more than N subs; 0 = disabled)")
    args = parser.parse_args()

    raw = (open(args.input).read().splitlines() if args.input
           else sys.stdin.read().splitlines())

    domains = sorted({normalize(l) for l in raw if normalize(l)})

    groups = defaultdict(set)
    for d in domains:
        groups[registrable_domain(d)].add(d)

    out = []
    for apex in sorted(groups.keys(), key=sort_key):
        if args.markdown:
            out.append(f"- {apex}")
        else:
            out.append(apex)
        apex_depth = len(apex.split("."))
        subs = sorted((d for d in groups[apex] if d != apex), key=sort_key)

        def emit(d: str, extra_depth: int):
            depth = len(d.split(".")) - apex_depth + extra_depth
            if args.markdown:
                out.append("  " * depth + f"- {d}")
            else:
                out.append("\t" * depth + d)

        if args.batch_size > 0 and len(subs) > args.batch_size:
            batches = [subs[i:i + args.batch_size]
                       for i in range(0, len(subs), args.batch_size)]
            for i, batch in enumerate(batches, 1):
                label = f"Batch {i:02d}"
                if args.markdown:
                    out.append("  " + f"- {label}")
                else:
                    out.append("\t" + label)
                for d in batch:
                    emit(d, 1)
        else:
            for d in subs:
                emit(d, 0)

    sep = "\n" * (args.newlines + 1)
    print(sep.join(out))


if __name__ == "__main__":
    main()
