#!/usr/bin/env python3

import ipaddress
import sys

def cidr_to_ips(cidr_range):
    """
    Convert a CIDR range to a list of IP addresses.

    :param cidr_range: A CIDR notation string (e.g., '1.1.1.1/22')
    :return: List of IP addresses in the given CIDR range
    """
    try:
        # Create a network object from the CIDR range
        network = ipaddress.ip_network(cidr_range, strict=False)

        # Generate and return list of all IP addresses in the network
        return [str(ip) for ip in network.hosts()]

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    # Check if CIDR range is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python3 " + sys.argv[0] + "<CIDR_RANGE>")
        print("Example: python3 " + sys.argv[0] + " 1.1.1.1/22")
        sys.exit(1)

    # Get CIDR range from command-line argument
    cidr_range = sys.argv[1]

    # Convert and print IPs
    ip_list = cidr_to_ips(cidr_range)

    # Print IPs (option to modify output format as needed)
    for ip in ip_list:
        print(ip)

if __name__ == "__main__":
    main()
