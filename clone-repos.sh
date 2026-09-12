#!/usr/bin/env bash
#
# clone-repos.sh — clone all repos of a GitHub org
#
# Usage:
#   ./clone-repos.sh [-t TOKEN] [-s] <org-url-or-name>
#

set -euo pipefail

API="https://api.github.com"
TOKEN=""
USE_SSH=0
SKIP_ARCHIVE=0
SKIP_FORK=0
GIT_FLAGS=""
ORG_INPUT=""

usage() {
    cat <<EOF
Usage: $(basename "$0") [-t TOKEN] [-s] [--skip-archive] [--skip-fork] [-g FLAGS] <org-url-or-name>

  -t, --token TOKEN   GitHub API token (or set \$GITHUB_TOKEN)
  -s, --ssh           Clone via SSH instead of HTTPS
  --skip-archive      Skip archived repos
  --skip-fork         Skip forked repos
  -g, --git-flags STR Raw flags appended to \`git clone\`, space-split as-is
                       (no shell quoting support — simple flags only)
  -h, --help          Show this help

Examples:
  $(basename "$0") https://github.com/orgs/<org-name>/
  $(basename "$0") -t ghp_xxx <org-name>
  GITHUB_TOKEN=ghp_xxx $(basename "$0") <org-name>
  $(basename "$0") -g "--depth 1 --single-branch" <org-name>
  $(basename "$0") --skip-archive --skip-fork <org-name>
EOF
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--token) TOKEN="${2:-}"; shift 2 ;;
        --token=*)  TOKEN="${1#*=}"; shift ;;
        -s|--ssh)   USE_SSH=1; shift ;;
        --skip-archive) SKIP_ARCHIVE=1; shift ;;
        --skip-fork)    SKIP_FORK=1; shift ;;
        -g|--git-flags) GIT_FLAGS="${2:-}"; shift 2 ;;
        --git-flags=*)  GIT_FLAGS="${1#*=}"; shift ;;
        -h|--help)  usage ;;
        -*)         echo "[-] unknown flag: $1" >&2; usage ;;
        *)          ORG_INPUT="$1"; shift ;;
    esac
done

[[ -z "$ORG_INPUT" ]] && usage
TOKEN="${TOKEN:-${GITHUB_TOKEN:-${GITHUB_API:-}}}"

for bin in curl jq git; do
    command -v "$bin" >/dev/null 2>&1 || { echo "[-] missing dependency: $bin" >&2; exit 1; }
done

ORG=$(printf '%s' "$ORG_INPUT" | sed -E 's#^(https?://)?(www\.)?github\.com/##; s#^orgs/##; s#/.*##; s#\.git$##')
[[ -z "$ORG" ]] && { echo "[-] couldn't parse org name from: $ORG_INPUT" >&2; exit 1; }

echo "[*] org: $ORG"
[[ -n "$TOKEN" ]] && echo "[*] authenticated requests" || echo "[*] no token — unauthenticated (60 req/hr)"

api_get() {
    local url="$1"
    local -a headers=(-H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28")
    [[ -n "$TOKEN" ]] && headers+=(-H "Authorization: Bearer $TOKEN")
    curl -sS -w '\n%{http_code}' "${headers[@]}" "$url"
}

PAGE=1
PER_PAGE=100
CLONE_URLS=()

URL_FIELD="clone_url"
[[ "$USE_SSH" -eq 1 ]] && URL_FIELD="ssh_url"

JQ_COND=""
[[ "$SKIP_ARCHIVE" -eq 1 ]] && JQ_COND+="${JQ_COND:+ and }.archived == false"
[[ "$SKIP_FORK" -eq 1 ]]    && JQ_COND+="${JQ_COND:+ and }.fork == false"
JQ_SELECT=".[]"
[[ -n "$JQ_COND" ]] && JQ_SELECT=".[] | select($JQ_COND)"

while :; do
    RESPONSE=$(api_get "$API/orgs/$ORG/repos?per_page=$PER_PAGE&page=$PAGE&type=all")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [[ "$HTTP_CODE" != "200" ]]; then
        MSG=$(echo "$BODY" | jq -r '.message // "unknown error"')
        echo "[-] api error ($HTTP_CODE): $MSG" >&2
        [[ "$HTTP_CODE" == "403" ]] && echo "[-] likely rate-limited — pass a token via -t or \$GITHUB_TOKEN" >&2
        exit 1
    fi

    COUNT=$(echo "$BODY" | jq 'length')
    [[ "$COUNT" -eq 0 ]] && break

    mapfile -t -O "${#CLONE_URLS[@]}" CLONE_URLS < <(echo "$BODY" | jq -r "$JQ_SELECT | .$URL_FIELD")

    [[ "$COUNT" -lt "$PER_PAGE" ]] && break
    PAGE=$((PAGE + 1))
done

TOTAL=${#CLONE_URLS[@]}
echo "[*] found $TOTAL repos"
[[ "$TOTAL" -eq 0 ]] && exit 0

FAIL=0
GIT_FLAG_ARR=()
[[ -n "$GIT_FLAGS" ]] && read -ra GIT_FLAG_ARR <<< "$GIT_FLAGS"

for url in "${CLONE_URLS[@]}"; do
    NAME=$(basename "$url" .git)
    if [[ -d "$NAME" ]]; then
        echo "[=] skip (exists): $NAME"
        continue
    fi
    echo "[+] cloning: $NAME"
    if ! ERR=$(git clone --quiet "$url" "${GIT_FLAG_ARR[@]}" 2>&1); then
        echo "[-] failed: $NAME — $ERR" >&2
        FAIL=$((FAIL + 1))
    fi
done

echo "[*] done — $((TOTAL - FAIL))/$TOTAL cloned"
[[ "$FAIL" -gt 0 ]] && exit 1
exit 0
