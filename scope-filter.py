#!/usr/bin/env python3
"""
Filters out-of-scope URLs

Usage:
    scopefilter.py -s scope.txt < urls.txt > in-scope.txt
    cat urls.txt | scopefilter.py -s scope.txt > in-scope.txt

"scope.txt" example:
```
maintarget.com      # matches the main domain + all levels subdomains
www.target.com      # matches starting from the `www.` subdomain and above - NOT `target.com` urls
```
"""
import argparse
import sys
from urllib.parse import urlsplit


def load_scope(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip().lower() for line in f if line.strip()]


def get_host(line: str) -> str | None:
    line = line.strip()
    if not line:
        return None
    target = line if "://" in line else "//" + line     # tolerate missing scheme
    host = urlsplit(target).hostname                    # None if unparseable, strips port
    return host.lower() if host else None


def in_scope(host: str, scope: list[str]) -> bool:
    return any(host == s or host.endswith("." + s) for s in scope)


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter stdin URLs against a scope list.")
    parser.add_argument("-s", "--scope", required=True, help="path to scope file (one domain per line)")
    args = parser.parse_args()

    scope = load_scope(args.scope)

    for line in sys.stdin:
        host = get_host(line)
        if host and in_scope(host, scope):
            sys.stdout.write(line.strip() + "\n")


if __name__ == "__main__":
    main()