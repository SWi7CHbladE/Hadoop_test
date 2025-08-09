#!/usr/bin/env python3
import sys

current_phone = None
products = []

for line in sys.stdin:                                              # The input provided to the reducer is through stdin.
    line = line.strip()                                             # Strip the line again in case any whitespaces got introduced.
    if not line:                                                    # Continue if not a valid line.
        continue
    phone, product = line.split("\t", 1)                            # Split the variables using '\t' as the delimiter set by the mapper function.

    if current_phone == phone:                                      # Check phone number by phone number, if the retrieved phone number = currently observed phone number, append the product to the product list.
        products.append(product)
    else:                                                           
        if current_phone:                                           # In case the phone number was set to none, set the retrieved phone number to currently observed phone number.
            print(f"{current_phone}\t{','.join(products)}")
        current_phone = phone
        products = [product]

# Final output
if current_phone:
    print(f"{current_phone}\t{','.join(products)}")                 # Print the output.
