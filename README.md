# DATABASE-PROJECT
Data project in python 2024/2025



# Paraná Shopping System

## Description
Paraná Shopping System is a simple command-line shopping application that allows users to browse products, add items to their basket, modify orders, and checkout. It uses an SQLite database to store order history, products, and shopper information.

## Features
- **User Authentication**: Validates shopper ID before allowing access.
- **Order History**: Displays previous purchases.
- **Shopping Basket**:
  - Add products to the basket
  - Modify item quantities
  - Remove items from the basket
  - View basket contents
- **Checkout System**: Finalizes the order and updates the database.
- **Database Connectivity**: Uses SQLite to manage products, orders, and user details.

## Technologies Used
- **Python** (Standard Libraries)
- **SQLite** (Database Management)

## Installation & Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
   ```
2. Navigate to the project directory:
   ```sh
   cd YOUR-REPO-NAME
   ```
3. Install dependencies (if any):
   ```sh
   pip install -r requirements.txt
   ```
4. Run the script:
   ```sh
   python Project_app.py
   ```

## Database Setup
- The application expects an SQLite database named `Assessment.db`.
- Ensure the database includes tables for shoppers, orders, products, and sellers.
- Example schema for the shoppers table:
  ```sql
  CREATE TABLE shoppers (
      shopper_id INTEGER PRIMARY KEY,
      shopper_first_name TEXT,
      shopper_surname TEXT
  );
  ```

## Usage Guide
1. Enter a valid shopper ID.
2. Navigate the menu using the numbered options.
3. Add products, modify quantities, and proceed to checkout.
4. View order history or exit the application.

## Future Improvements
- Implement a GUI for better user experience.
- Add online payment integration.
- Implement user authentication with login credentials.

## License
This project is open-source and available under the MIT License.

## Author
Dawid Wnetrzak

---
For any questions or contributions, feel free to open an issue or submit a pull request.

