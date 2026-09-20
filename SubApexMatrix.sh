#!/usr/bin/env bash
# Usage: ./SubApexMatrix.sh subs.txt apexes.txt
#		subs.txt:		www, us, ar, api, staging, ...
#		apexes.txt:		target.com, target.co.uk, target.com.mx, target.tw, target.in

if [[ $# -ne 2 || ! -f "$1" || ! -f "$2" ]]; then
  echo "Usage: $0 subs.txt apexes.txt" >&2
  exit 1
fi

subs="$1"
apexes="$2"

while read -r apex; do
  while read -r sub; do
    echo "${sub}.${apex}"
  done < "$subs"
done < "$apexes"
