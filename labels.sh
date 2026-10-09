#!/usr/bin/env bash
# extract unique subdomain labels/keywords from a list of domains
# input: list of subdomains
# output: subdomain wordlist
# Usage:
#	labels domains.txt > words.txt          # file
#	cat domains.txt | labels > words.txt    # stdin
#	labels -d domains.txt                   # also split on dashes
#	labels -n 3 uk-domains.txt              # strip 3 labels (example.co.uk)

set -euo pipefail

usage() {
  cat >&2 << 'USAGE'
Usage: labels [-n N] [-d] [file ...]
  -n N   labels to strip from the right as the apex (default: 2)
  -d     also split labels on dashes (media-router -> media, router)
  -h     help
Reads stdin if no file is given.
USAGE
  exit "${1:-0}"
}

n=2 d=0
while getopts "n:dh" opt; do
  case $opt in
    n) n=$OPTARG ;;
    d) d=1 ;;
    h) usage 0 ;;
    *) usage 1 ;;
  esac
done
shift $((OPTIND - 1))

[[ $n =~ ^[0-9]+$ ]] || { echo "labels: -n must be a number" >&2; exit 1; }

exec awk -F. -v n="$n" -v d="$d" '
  { gsub(/\r/, ""); $0 = tolower($0); sub(/^\*\./, "") }
  {
    for (i = 1; i <= NF - n; i++) {
      l = $i
      if (l == "" || l ~ /[*]/) continue
      if (!s[l]++) print l
      if (d) {
        k = split(l, p, "-")
        if (k > 1) for (j = 1; j <= k; j++) if (p[j] != "" && !s[p[j]]++) print p[j]
      }
    }
  }' "$@"
