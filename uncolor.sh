#!/bin/bash
# Remove ANSI escape sequences and control chars from input

sed -r 's/\x1B\[[0-9;]*[a-zA-Z]//g' | tr -d '\r'
