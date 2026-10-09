labels() {
# input: list of subdomains
# output: subdomain wordlist
# Usage:
#	labels domains.txt > words.txt          # file
#	cat domains.txt | labels > words.txt    # stdin
#	labels -d domains.txt                   # also split on dashes
#	labels -n 3 uk-domains.txt              # strip 3 labels (example.co.uk)

  local n=2 d=0 opt OPTIND=1
  while getopts "n:d" opt; do
    case $opt in n) n=$OPTARG ;; d) d=1 ;; esac
  done
  shift $((OPTIND-1))

  awk -F. -v n="$n" -v d="$d" '
    { gsub(/\r/,""); $0=tolower($0); sub(/^\*\./,"") }
    {
      for (i=1; i<=NF-n; i++) {
        l=$i
        if (l=="" || l ~ /[*]/) continue
        if (!s[l]++) print l
        if (d) {
          k=split(l, p, "-")
          if (k>1) for (j=1; j<=k; j++) if (p[j]!="" && !s[p[j]]++) print p[j]
        }
      }
    }' "$@"
}
