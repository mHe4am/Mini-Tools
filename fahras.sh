#!/bin/bash

# Default values
output_file="wordlist.txt"
min_length=3
max_length=25
include_numbers=0
include_extensions=0
verbose=0

print_help() {
    cat << EOF
Usage: $0 [options] <input_files...>

Options:
    -o, --output FILE       Output file (default: wordlist.txt)
    -m, --min-length NUM    Minimum word length (default: 3)
    -M, --max-length NUM    Maximum word length (default: 25)
    -n, --numbers          Include numbers in output
    -e, --extensions       Include filenames with extensions
    -v, --verbose          Verbose output
    -h, --help            Show this help message

Example:
    $0 -o custom_wordlist.txt -m 4 burp_urls.txt wayback_urls.txt
    $0 -v -n urls/*.txt
EOF
}

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            output_file="$2"
            shift 2
            ;;
        -m|--min-length)
            min_length="$2"
            shift 2
            ;;
        -M|--max-length)
            max_length="$2"
            shift 2
            ;;
        -n|--numbers)
            include_numbers=1
            shift
            ;;
        -e|--extensions)
            include_extensions=1
            shift
            ;;
        -v|--verbose)
            verbose=1
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            break
            ;;
    esac
done

if [ $# -eq 0 ]; then
    echo "Error: No input files specified"
    print_help
    exit 1
fi

# Check if unfurl is installed
if ! command -v unfurl &> /dev/null; then
    echo "Error: unfurl is not installed. Please install it first:"
    echo "go install github.com/tomnomnom/unfurl@latest"
    exit 1
fi

# Common file extensions to filter if --extensions is not enabled
extensions="html|htm|php|asp|aspx|jsp|png|jpg|jpeg|gif|bmp|svg|js|css|pdf|xml|json|woff|ttf|eot|ico|txt|doc|docx|xls|xlsx|zip|tar|gz|rar"

# Function to log verbose messages
log() {
    if [ $verbose -eq 1 ]; then
        echo "[*] $1" >&2
    fi
}

# Create temporary file
temp_file=$(mktemp)
trap 'rm -f $temp_file' EXIT

log "Starting processing..."
total_files=$#
processed_files=0

# Process each input file
for input_file in "$@"; do
    if [ ! -f "$input_file" ]; then
        echo "Warning: File not found: $input_file" >&2
        continue
    fi
    
    processed_files=$((processed_files + 1))
    log "Processing file $processed_files/$total_files: $input_file"
    
    if [ $include_extensions -eq 1 ]; then
        # Process with extensions
        cat "$input_file" | \
            unfurl -u paths | \
            sed 's#/#\n#g' >> "$temp_file"
    else
        # Process without extensions
        cat "$input_file" | \
            unfurl -u paths | \
            sed 's#/#\n#g' | \
            grep -ivE "\.(${extensions})$" | \
            sed -E 's/\.[^.]+$//' >> "$temp_file"
    fi
done

# Final processing
cat "$temp_file" | \
    grep -v '^$' | \
    tr '[:upper:]' '[:lower:]' | \
    grep -E "^.{$min_length,$max_length}$" | \
    if [ $include_numbers -eq 0 ]; then
        grep -v "[0-9]"
    else
        cat
    fi | \
    sort | uniq -c | sort -rn | \
    awk '{print $2}' > "$output_file"

total_words=$(wc -l < "$output_file")
log "Found $total_words unique words"
echo "Successfully generated wordlist with $total_words words in $output_file"
