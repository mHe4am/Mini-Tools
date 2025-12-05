#!/usr/bin/env python3
import sys
from urllib.parse import urlparse
from tqdm import tqdm

def extract_domains(input_file, output_file):
    domains = set()
    total_lines = sum(1 for _ in open(input_file, 'r'))

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in tqdm(infile, total=total_lines, desc="Processing URLs"):
            try:
                parsed_url = urlparse(line.strip())
                domain = parsed_url.netloc
                if domain:
                    domains.add(domain)
            except Exception as e:
                print(f"Error processing URL: {line.strip()}", file=sys.stderr)

        for domain in sorted(domains):
            outfile.write(f"{domain}\n")

    print(f"Extracted {len(domains)} unique domains.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    extract_domains(input_file, output_file)
