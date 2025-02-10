import sqlite3

# Database path
DB_PATH = "Assessment.db"


# ---------------- 1. MENU ----------------
def main_menu():
    """Displays the main menu."""
    print("\n=== PARANÁ – SHOPPER MAIN MENU ===")
    print("1. Display your order history")
    print("2. Add an item to your basket")
    print("3. View your basket")
    print("4. Change the quantity of an item in your basket")
    print("5. Remove an item from your basket")
    print("6. Checkout")
    print("7. Exit")


# ---------------- 2. DATABASE FUNCTIONS ----------------
def get_shopper_name(shopper_id):
    """Check if shopper_id exists and return their full name."""
    try:
        # Connect to the database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Query to check if shopper_id exists
        query = "SELECT shopper_first_name, shopper_surname FROM shoppers WHERE shopper_id = ?"
        cursor.execute(query, (shopper_id,))
        result = cursor.fetchone()  # Fetch one result

        # Close the connection
        connection.close()

        # If shopper exists, return full name
        if result:
            return f"{result[0]} {result[1]}"
        else:
            return None  # Shopper not found

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


def display_order_history(shopper_id):
    """Retrieve and display the order history for a given shopper."""
    try:
        # Connect to the database
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # SQL query
        query = '''
        SELECT o.order_id, o.order_date, p.product_description, s.seller_name, 
               op.price, op.quantity, op.ordered_product_status
        FROM shopper_orders o
        JOIN ordered_products op ON o.order_id = op.order_id
        JOIN products p ON op.product_id = p.product_id
        JOIN sellers s ON op.seller_id = s.seller_id
        WHERE o.shopper_id = ?
        ORDER BY o.order_date DESC;
        '''

        # Execute the query
        cursor.execute(query, (shopper_id,))
        results = cursor.fetchall()

        # Close the database connection
        connection.close()

        # If there are no orders, print a message
        if not results:
            print("\nNo orders placed by this customer.")
            return

        # Print order history
        print("\n=== Order History ===")
        print("=" * 90)
        print("{:<10} {:<15} {:<30} {:<15} {:<10} {:<10} {:<10}".format(
            "Order ID", "Order Date", "Product", "Seller", "Price", "Qty", "Status"
        ))
        print("-" * 90)

        for row in results:
            order_id, order_date, product_desc, seller_name, price, quantity, status = row
            print("{:<10} {:<15} {:<30} {:<15} {:<10} {:<10} {:<10}".format(
                order_id, order_date, product_desc[:27], seller_name[:12], price, quantity, status
            ))

        print("\nReturning to the main menu...")

    except sqlite3.Error as e:
        print(f"Database error: {e}")


def choose_category(cursor):
    """Display product categories and let the user choose one."""
    print("\n=== Product Categories ===")
    cursor.execute("SELECT category_id, category_description FROM categories ORDER BY category_description;")
    categories = cursor.fetchall()

    if not categories:
        print("No categories available.")
        return None

    for idx, category in enumerate(categories, start=1):
        print(f"{idx}. {category[1]}")

    choice = int(input("Enter category number: ")) - 1
    return categories[choice][0] if 0 <= choice < len(categories) else None


def choose_product(cursor, category_id):
    """Display products in a category and let the user choose one."""
    print("\n=== Available Products ===")
    cursor.execute("SELECT product_id, product_description FROM products WHERE category_id = ? ORDER BY product_description;", (category_id,))
    products = cursor.fetchall()

    if not products:
        print("No products available in this category.")
        return None

    for idx, product in enumerate(products, start=1):
        print(f"{idx}. {product[1]}")

    choice = int(input("Enter product number: ")) - 1
    return products[choice][0] if 0 <= choice < len(products) else None


def choose_seller(cursor, product_id):
    """Display available sellers and let the user choose one."""
    print("\n=== Available Sellers ===")
    cursor.execute("SELECT s.seller_id, s.seller_name, ps.price FROM product_sellers ps JOIN sellers s ON ps.seller_id = s.seller_id WHERE ps.product_id = ? ORDER BY s.seller_name;", (product_id,))
    sellers = cursor.fetchall()

    if not sellers:
        print("No sellers available for this product.")
        return None, None

    for idx, seller in enumerate(sellers, start=1):
        print(f"{idx}. {seller[1]} - ${seller[2]}")

    choice = int(input("Enter seller number: ")) - 1
    return (sellers[choice][0], sellers[choice][2]) if 0 <= choice < len(sellers) else (None, None)


def get_or_create_basket(cursor, shopper_id):
    """Check if the shopper has an active basket or create a new one."""
    cursor.execute("""
        SELECT basket_id FROM shopper_baskets 
        WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now') 
        ORDER BY basket_created_date_time DESC LIMIT 1;
    """, (shopper_id,))
    basket = cursor.fetchone()

    if basket:
        return basket[0]

    cursor.execute("INSERT INTO shopper_baskets (shopper_id, basket_created_date_time) VALUES (?, datetime('now')) RETURNING basket_id;", (shopper_id,))
    return cursor.fetchone()[0]


def add_item_to_basket(shopper_id):
    """Main function to add an item to the shopper's basket."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        category_id = choose_category(cursor)
        if not category_id:
            return

        product_id = choose_product(cursor, category_id)
        if not product_id:
            return

        seller_id, price = choose_seller(cursor, product_id)
        if not seller_id:
            return

        while True:
            quantity = int(input("Enter quantity (must be greater than 0): "))
            if quantity > 0:
                break
            print("Quantity must be greater than 0.")

        basket_id = get_or_create_basket(cursor, shopper_id)

        cursor.execute("INSERT INTO basket_contents (basket_id, product_id, seller_id, quantity, price) VALUES (?, ?, ?, ?, ?);",
                       (basket_id, product_id, seller_id, quantity, price))

        connection.commit()
        print("\n✅ Item added to your basket!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
    finally:
        connection.close()


def view_basket(shopper_id):
    """Display all items in the shopper's basket."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Retrieve the most recent active basket for the shopper
        cursor.execute("""
            SELECT basket_id FROM shopper_baskets
            WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now')
            ORDER BY basket_created_date_time DESC LIMIT 1;
        """, (shopper_id,))
        basket = cursor.fetchone()

        if not basket:
            print("\nYour basket is empty.")
            return

        basket_id = basket[0]

        # Retrieve basket contents
        cursor.execute("""
            SELECT p.product_description, s.seller_name, bc.quantity, bc.price
            FROM basket_contents bc
            JOIN products p ON bc.product_id = p.product_id
            JOIN sellers s ON bc.seller_id = s.seller_id
            WHERE bc.basket_id = ?;
        """, (basket_id,))
        items = cursor.fetchall()

        if not items:
            print("\nYour basket is empty.")
            return

        # Display basket contents
        print("\n=== Your Basket ===")
        print("=" * 60)
        print("{:<30} {:<15} {:<10} {:<10}".format("Product", "Seller", "Qty", "Price"))
        print("-" * 60)

        total_cost = 0
        for product_desc, seller_name, quantity, price in items:
            print("{:<30} {:<15} {:<10} ${:<10.2f}".format(
                product_desc[:27], seller_name[:12], quantity, price * quantity
            ))
            total_cost += price * quantity

        print("-" * 60)
        print(f"Total: ${total_cost:.2f}")
        print("=" * 60)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()


def change_quantity(shopper_id):
    """Change the quantity of an item in the shopper's basket."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Retrieve the most recent active basket for the shopper
        cursor.execute("""
            SELECT basket_id FROM shopper_baskets
            WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now')
            ORDER BY basket_created_date_time DESC LIMIT 1;
        """, (shopper_id,))
        basket = cursor.fetchone()

        if not basket:
            print("\nYour basket is empty.")
            return

        basket_id = basket[0]

        # Retrieve basket contents
        cursor.execute("""
            SELECT bc.product_id, p.product_description, s.seller_name, bc.quantity, bc.price
            FROM basket_contents bc
            JOIN products p ON bc.product_id = p.product_id
            JOIN sellers s ON bc.seller_id = s.seller_id
            WHERE bc.basket_id = ?;
        """, (basket_id,))
        items = cursor.fetchall()

        if not items:
            print("\nYour basket is empty.")
            return

        # Display basket contents
        print("\n=== Your Basket ===")
        for idx, (product_id, product_desc, seller_name, quantity, price) in enumerate(items, start=1):
            print(f"{idx}. {product_desc[:27]} ({seller_name}) - Qty: {quantity}, Price: ${price:.2f}")

        # Select an item to change quantity
        item_choice = int(input("Enter the number of the item you want to modify: ")) - 1
        if item_choice < 0 or item_choice >= len(items):
            print("Invalid choice.")
            return

        selected_product_id = items[item_choice][0]

        # Enter new quantity
        while True:
            new_quantity = int(input("Enter the new quantity (must be greater than 0): "))
            if new_quantity > 0:
                break
            print("Quantity must be greater than 0.")

        # Update the basket contents
        cursor.execute("""
            UPDATE basket_contents
            SET quantity = ?
            WHERE basket_id = ? AND product_id = ?;
        """, (new_quantity, basket_id, selected_product_id))

        connection.commit()
        print("\n✅ Quantity updated successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
    finally:
        connection.close()


def remove_item(shopper_id):
    """Remove an item from the shopper's basket."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Retrieve the most recent active basket for the shopper
        cursor.execute("""
            SELECT basket_id FROM shopper_baskets
            WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now')
            ORDER BY basket_created_date_time DESC LIMIT 1;
        """, (shopper_id,))
        basket = cursor.fetchone()

        if not basket:
            print("\nYour basket is empty.")
            return

        basket_id = basket[0]

        # Retrieve basket contents
        cursor.execute("""
            SELECT bc.product_id, p.product_description, s.seller_name, bc.quantity, bc.price
            FROM basket_contents bc
            JOIN products p ON bc.product_id = p.product_id
            JOIN sellers s ON bc.seller_id = s.seller_id
            WHERE bc.basket_id = ?;
        """, (basket_id,))
        items = cursor.fetchall()

        if not items:
            print("\nYour basket is empty.")
            return

        # Display basket contents
        print("\n=== Your Basket ===")
        for idx, (product_id, product_desc, seller_name, quantity, price) in enumerate(items, start=1):
            print(f"{idx}. {product_desc[:27]} ({seller_name}) - Qty: {quantity}, Price: ${price:.2f}")

        # Select an item to remove
        item_choice = int(input("Enter the number of the item you want to remove: ")) - 1
        if item_choice < 0 or item_choice >= len(items):
            print("Invalid choice.")
            return

        selected_product_id = items[item_choice][0]

        # Confirm removal
        confirm = input("Are you sure you want to remove this item? (Y/N): ").strip().lower()
        if confirm != 'y':
            print("Item not removed.")
            return

        # Remove the selected item from the basket
        cursor.execute("""
            DELETE FROM basket_contents
            WHERE basket_id = ? AND product_id = ?;
        """, (basket_id, selected_product_id))

        connection.commit()
        print("\n✅ Item removed successfully!")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
    finally:
        connection.close()


def checkout(shopper_id):
    """Proceed with the checkout process."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Retrieve the most recent active basket for the shopper
        cursor.execute("""
            SELECT basket_id FROM shopper_baskets
            WHERE shopper_id = ? AND DATE(basket_created_date_time) = DATE('now')
            ORDER BY basket_created_date_time DESC LIMIT 1;
        """, (shopper_id,))
        basket = cursor.fetchone()

        if not basket:
            print("\nYour basket is empty. Nothing to checkout.")
            return

        basket_id = basket[0]

        # Retrieve basket contents
        cursor.execute("""
            SELECT bc.product_id, bc.seller_id, p.product_description, s.seller_name, bc.quantity, bc.price
            FROM basket_contents bc
            JOIN products p ON bc.product_id = p.product_id
            JOIN sellers s ON bc.seller_id = s.seller_id
            WHERE bc.basket_id = ?;
        """, (basket_id,))
        items = cursor.fetchall()

        if not items:
            print("\nYour basket is empty. Nothing to checkout.")
            return

        # Display order summary
        print("\n=== Order Summary ===")
        total_cost = 0
        for product_id, seller_id, product_desc, seller_name, quantity, price in items:
            item_total = quantity * price
            total_cost += item_total
            print(f"{product_desc[:27]} ({seller_name}) - Qty: {quantity}, Total: ${item_total:.2f}")

        print(f"\nTotal Cost: ${total_cost:.2f}")
        confirm = input("Proceed with checkout? (Y/N): ").strip().lower()
        if confirm != 'y':
            print("Checkout canceled.")
            return

        # Insert order into shopper_orders
        cursor.execute("""
            INSERT INTO shopper_orders (shopper_id, order_date, order_status)
            VALUES (?, datetime('now'), 'Placed') RETURNING order_id;
        """, (shopper_id,))
        order_id = cursor.fetchone()[0]

        # Move items from basket to ordered_products
        for product_id, seller_id, _, _, quantity, price in items:
            cursor.execute("""
                INSERT INTO ordered_products (order_id, product_id, seller_id, quantity, price, ordered_product_status)
                VALUES (?, ?, ?, ?, ?, 'Placed');
            """, (order_id, product_id, seller_id, quantity, price))

        # Clear the basket after checkout
        cursor.execute("DELETE FROM basket_contents WHERE basket_id = ?;", (basket_id,))
        cursor.execute("DELETE FROM shopper_baskets WHERE basket_id = ?;", (basket_id,))

        connection.commit()
        print("\n✅ Checkout complete! Your order has been placed.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        connection.rollback()
    finally:
        connection.close()


# ---------------- 3. MAIN PROGRAM LOOP ----------------
def main():
    """Main function to start the program."""
    print("\nWelcome to Paraná Shopping System!")

    # Ask for shopper ID
    shopper_id = input("Enter your shopper ID: ")

    # Validate shopper ID
    shopper = get_shopper_name(shopper_id)
    if not shopper:
        print("Error: Shopper ID not found. Exiting program.")
        return  # Exit program if ID does not exist

    print(f"Welcome, {shopper}!")

    while True:
        main_menu()
        choice = input("Choose an option (1-7): ")

        if choice == "1":
            display_order_history(shopper_id)
        elif choice == "2":
            add_item_to_basket(shopper_id)
        elif choice == "3":
            view_basket(shopper_id)
        elif choice == "4":
            change_quantity(shopper_id)
        elif choice == "5":
            remove_item(shopper_id)
        elif choice == "6":
            checkout(shopper_id)
        elif choice == "7":
            print("\nExiting the program. Goodbye!")
            break  # Exit program loop
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


# ---------------- 4. START PROGRAM ----------------
if __name__ == "__main__":
    main()
