#!/bin/bash
# Remove ANSI color escape sequences from input

sed -r 's/\x1B\[[0-9;]*[mK]//g'
