import random
import pandas as pd

def generate_random_data(start_phone, end_phone, products, num_rows):
    """
    Generates a DataFrame with random combinations of phone numbers and products.

    Args:
        start_phone (int): The starting phone number of the range.
        end_phone (int): The ending phone number of the range.
        products (list): A list of product strings.
        num_rows (int): The number of rows of data to generate.

    Returns:
        pandas.DataFrame: A DataFrame containing the generated data with
                          'PhoneNumber' and 'Product' columns.
                          Returns None if inputs are invalid.
    """
    # --- Input Validation ---
    if not all([
        isinstance(start_phone, int),
        isinstance(end_phone, int),
        isinstance(products, list),
        isinstance(num_rows, int)
    ]):
        print("Error: Please provide valid input types.")
        return None

    if start_phone >= end_phone:
        print("Error: The starting phone number must be less than the ending phone number.")
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

    for _ in range(num_rows):
        # Generate a random phone number within the specified range
        random_phone = random.randint(start_phone, end_phone)

        # Choose a random product from the list
        random_product = random.choice(products)

        # Append the combination to our data list
        data.append({
            'PhoneNumber': random_phone,
            'Product': random_product
        })

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(data)
    return df

# --- Example Usage ---
if __name__ == "__main__":
    # --- Define Your Inputs Here ---

    # 1. Define the phone number range
    # Example: From 9876543210 to 9876553210
    phone_range_start = 9876543210
    phone_range_end = 9876543310

    # 2. Define the set of products
    product_list = [
        "Laptop",
        "Mouse",
        "Keyboard",
        "Monitor",
        "USB Hub",
        "Smartphone",
        "Milk",
        "Hammer",
        "Fertilizer",
        "Detergent",
        "Biscuit"
    ]

    # 3. Define the number of rows you want to generate
    number_of_rows_to_generate = 100000

    # --- Generate and Display the Data ---
    generated_df = generate_random_data(
        start_phone=phone_range_start,
        end_phone=phone_range_end,
        products=product_list,
        num_rows=number_of_rows_to_generate
    )

    if generated_df is not None:
        print("\n--- Generated Data Sample ---")
        # Display the first 10 rows of the generated DataFrame
        print(generated_df.head(10))

        # --- Optional: Save the DataFrame to a CSV file ---
        try:
            output_filename = "generated_data.csv"
            generated_df.to_csv(output_filename, index=False)
            print(f"\nSuccessfully saved all {len(generated_df)} rows to '{output_filename}'")
        except Exception as e:
            print(f"\nError saving to CSV: {e}")
