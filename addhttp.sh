#!/bin/bash

# Function to print usage
print_usage() {
    echo "Usage: $0 [-i <file>] [--http] [-b]" >&2
    echo "Options:" >&2
    echo "  -i <file>  Input file (if not provided, reads from stdin)" >&2
    echo "  --http     Use http:// instead of https://" >&2
    echo "  -b         Output both http:// and https:// versions" >&2
    exit 1
}

# Function to add scheme to URLs
add_scheme() {
    local url="$1"
    local use_http="$2"
    local use_both="$3"

    # Skip empty lines
    [ -z "$url" ] && return

    # If URL already has a scheme, output as-is
    if [[ $url =~ ^https?:// ]]; then
        echo "$url"
        return
    fi

    # Add appropriate scheme(s)
    if [ "$use_both" = true ]; then
        echo "http://$url"
        echo "https://$url"
    elif [ "$use_http" = true ]; then
        echo "http://$url"
    else
        echo "https://$url"
    fi
}

# Initialize variables
use_http=false
use_both=false
input_file=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i)
            if [[ -n "$2" ]]; then
                input_file="$2"
                shift 2
            else
                echo "Error: -i requires an input file" >&2
                print_usage
            fi
            ;;
        --http)
            use_http=true
            shift
            ;;
        -b)
            use_both=true
            shift
            ;;
        *)
            echo "Invalid option: $1" >&2
            print_usage
            ;;
    esac
done

# Process input
process_input() {
    while IFS= read -r line || [ -n "$line" ]; do
        add_scheme "$line" "$use_http" "$use_both"
    done
}

# Handle input source
if [ -n "$input_file" ]; then
    # Check if the input file exists
    if [ ! -f "$input_file" ]; then
        echo "Error: File not found: $input_file" >&2
        exit 1
    fi
    process_input < "$input_file"
elif [ ! -t 0 ]; then
    # Reading from stdin (pipe or redirect)
    process_input
else
    print_usage
fi