#!/usr/bin/env python3
import re
import sys

def extract_subdomains(amass_output, base_domain):
    """
    Extract subdomains from amass output for a given base domain.
    
    Args:
        amass_output (str): The raw output from amass
        base_domain (str): The base domain to extract subdomains for (e.g., 'example.com')
        
    Returns:
        list: Sorted list of unique subdomains
    """
    # Clean the base domain input
    base_domain = base_domain.strip().lower()
    
    # Set to store unique subdomains
    subdomains = set()
    
    # Regular expression to match FQDN entries
    pattern = rf"((?:[a-zA-Z0-9-]+\.)*{re.escape(base_domain)})\s+\(FQDN\)"
    
    # Extract subdomains from each line
    for line in amass_output.split('\n'):
        match = re.search(pattern, line)
        if match:
            subdomain = match.group(1)
            subdomains.add(subdomain)
    
    return sorted(subdomains)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py [base_domain]")
        print("Example: python script.py example.com")
        sys.exit(1)
    
    base_domain = sys.argv[1]
    
    # Read amass output from stdin
    amass_output = sys.stdin.read()
    
    # Extract and print subdomains
    subdomains = extract_subdomains(amass_output, base_domain)
    
    # Print results
    for subdomain in subdomains:
        print(subdomain)

if __name__ == "__main__":
    main()
