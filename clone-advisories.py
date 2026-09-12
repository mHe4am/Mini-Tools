#!/usr/bin/env python3
"""
Fetch all published GitHub security advisories for a repo and save each as a markdown file.

Usage:
    python clone-advisories.py <github-advisories-url>
    python clone-advisories.py <url> --token ghp_xxx
    GITHUB_TOKEN=ghp_xxx python clone-advisories.py <url>

Output: one .md file per advisory, saved to the current working directory.

Generate a token (optional — raises rate limit from 60 → 5000 req/hr):
    github.com → Settings → Developer settings → Personal access tokens (classic)
    → Generate new token → no scopes needed for public repos

Examples:
    python clone-advisories.py https://github.com/<org>/<repo>/security/advisories
    python clone-advisories.py https://github.com/<org>/<repo>/security/advisories/<GHSA>   # will fetch all advisories for the repo, not just the single GHSA
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
import argparse


def parse_repo(url: str) -> str:
    m = re.match(r"https://github\.com/([^/]+/[^/]+)", url)
    if not m:
        sys.exit(f"[!] Can't parse owner/repo from: {url}")
    return m.group(1)


def sanitize(name: str) -> str:
    """Strip characters that are invalid in filenames across major OSes."""
    return re.sub(r'[<>:"/\\|?*\n\r\t]', "-", name).strip(" .")


def api_get(url: str, token: str | None = None) -> list | dict:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if e.code == 403 and "rate limit" in body.lower():
            sys.exit("[!] Rate limited. Set GITHUB_TOKEN or pass --token.")
        sys.exit(f"[!] GitHub API {e.code}: {body}")


def fetch_all(repo: str, token: str | None = None) -> list[dict]:
    results = []
    page = 1
    while True:
        url = (
            f"https://api.github.com/repos/{repo}/security-advisories"
            f"?state=published&per_page=100&page={page}"
        )
        batch = api_get(url, token)
        # GitHub can return HTTP 200 with a JSON error message (e.g. shared-IP rate limit)
        if isinstance(batch, dict):
            msg = batch.get("message", "Unknown error")
            hint = " Set GITHUB_TOKEN or pass --token." if "rate limit" in msg.lower() else ""
            sys.exit(f"[!] GitHub API error: {msg}{hint}")
        results.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return results


def save(adv: dict, out_dir: str = ".") -> str:
    severity = (adv.get("severity") or "unknown").lower()
    title    = (adv.get("summary") or adv.get("ghsa_id") or "untitled").strip()
    desc     = (adv.get("description") or "").strip()
    link     = adv.get("html_url", "")
    ghsa     = adv.get("ghsa_id", "")

    base     = sanitize(f"{severity} - {title}")
    filename = f"{base}.md"
    path     = os.path.join(out_dir, filename)

    # Disambiguate collisions with GHSA ID suffix
    if os.path.exists(path):
        filename = f"{base} [{ghsa}].md"
        path     = os.path.join(out_dir, filename)

    content = f"> **Advisory:** <{link}>\n\n{desc}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("url", help="GitHub security advisories URL (repo or specific GHSA)")
    ap.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub PAT (or set GITHUB_TOKEN env var)",
    )
    args = ap.parse_args()

    repo  = parse_repo(args.url)
    token = args.token

    print(f"[*] Repo  : {repo}")
    print(f"[*] Token : {'set' if token else 'not set  ← 60 req/hr limit applies'}")
    print(f"[*] Fetching published advisories...\n")

    advisories = fetch_all(repo, token)

    if not advisories:
        print("[*] No published advisories found.")
        return

    print(f"[+] {len(advisories)} advisories found\n")

    counts = {}
    for adv in advisories:
        fname = save(adv)
        sev   = (adv.get("severity") or "unknown").lower()
        counts[sev] = counts.get(sev, 0) + 1
        print(f"  [{sev:8}] {fname}")

    print(f"\n[+] Done — {len(advisories)} files saved to {os.path.abspath('.')}")
    print(f"    Breakdown: {', '.join(f'{v} {k}' for k, v in sorted(counts.items()))}")


if __name__ == "__main__":
    main()
