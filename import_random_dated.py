import random
import pandas as pd
from datetime import date, timedelta # Import date and timedelta

def generate_random_data(start_phone, end_phone, products, num_rows, start_date, end_date): # Add date parameters
    """
    Generates a DataFrame with random combinations of phone numbers, products, and purchase dates.

    Args:
        start_phone (int): The starting phone number of the range.
        end_phone (int): The ending phone number of the range.
        products (list): A list of product strings.
        num_rows (int): The number of rows of data to generate.
        start_date (datetime.date): The start date for the purchase date range.
        end_date (datetime.date): The end date for the purchase date range.

    Returns:
        pandas.DataFrame: A DataFrame containing the generated data with
                          'PhoneNumber', 'Product', and 'PurchaseDate' columns.
                          Returns None if inputs are invalid.
    """
    # --- Input Validation ---
    if not all([
        isinstance(start_phone, int),
        isinstance(end_phone, int),
        isinstance(products, list),
        isinstance(num_rows, int),
        isinstance(start_date, date), # Add validation for start_date
        isinstance(end_date, date)    # Add validation for end_date
    ]):
        print("Error: Please provide valid input types.")
        return None

    if start_phone >= end_phone:
        print("Error: The starting phone number must be less than the ending phone number.")
        return None

    # --- New validation for dates ---
    if start_date >= end_date:
        print("Error: The start_date must be before the end_date.")
        return None

    if not products:
        print("Error: The products list cannot be empty.")
        return None

    if num_rows <= 0:
        print("Error: The number of rows must be a positive integer.")
        return None

    # --- Data Generation ---
    data = []
    print(f"Generating {num_rows} rows of data...")

    # --- New: Calculate the time delta for random date generation ---
    date_range_in_days = (end_date - start_date).days

    for _ in range(num_rows):
        # Generate a random phone number within the specified range
        random_phone = random.randint(start_phone, end_phone)

        # Choose a random product from the list
        random_product = random.choice(products)

        # --- New: Generate a random date within the specified range ---
        random_days_to_add = random.randrange(date_range_in_days + 1)
        random_purchase_date = start_date + timedelta(days=random_days_to_add)

        # Append the combination to our data list
        data.append({
            'PhoneNumber': random_phone,
            'Product': random_product,
            'PurchaseDate': random_purchase_date # Add the new date field
        })

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)
    return df

# --- Example Usage ---
if __name__ == "__main__":
    # --- Define Your Inputs Here ---

    # 1. Define the phone number range
    phone_range_start = 9876543210
    phone_range_end = 9876543310

    # 2. Define the set of products
    product_list = [
        "Laptop", "Mouse", "Keyboard", "Monitor", "USB Hub", "Smartphone",
        "Milk", "Hammer", "Fertilizer", "Detergent", "Biscuit"
    ]

    # 3. Define the number of rows you want to generate
    number_of_rows_to_generate = 100000
    
    # 4. --- New: Define the purchase date range ---
    # Example: From January 1, 2024 to December 31, 2024
    purchase_date_start = date(2024, 1, 1)
    purchase_date_end = date(2024, 12, 31)


    # --- Generate and Display the Data ---
    generated_df = generate_random_data(
        start_phone=phone_range_start,
        end_phone=phone_range_end,
        products=product_list,
        num_rows=number_of_rows_to_generate,
        start_date=purchase_date_start, # Pass the start date
        end_date=purchase_date_end      # Pass the end date
    )

    if generated_df is not None:
        print("\n--- Generated Data Sample ---")
        # Display the first 10 rows of the generated DataFrame
        print(generated_df.head(10))

        # --- Optional: Save the DataFrame to a CSV file ---
        try:
            output_filename = "generated_data_with_dates.csv"
            generated_df.to_csv(output_filename, index=False)
            print(f"\nSuccessfully saved all {len(generated_df)} rows to '{output_filename}'")
        except Exception as e:
            print(f"\nError saving to CSV: {e}")
