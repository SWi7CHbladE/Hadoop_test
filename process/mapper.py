#!/usr/bin/env python3
import sys

for line in sys.stdin:                      # The input provided to the mapper is through stdin.
    line = line.strip()                     # This will remove any leading or trailing whitespaces.
    if not line:                            # Incase the line is invalid, skip onto the next line.
        continue
    if line.startswith("PhoneNumber"):      # Skip header if present.
        continue
    phone, product = line.split(",", 1)     # As the file is a csv, the phone and product can be separated by splitting them by the ',' (comma) symbol.
    print(f"{phone}\t{product}")            # Print the phone_number and the product.
# The output of the mapper will then be fed to the reducer using the stdin.
