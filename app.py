import streamlit as st
import mysql.connector
import xml.etree.ElementTree as ET

# Function to connect to the database
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="hello",
        database="my_database"
    )
# Function to connect to the database
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="hello",
            database="my_database"
        )

        # Check and create tables if not exist
        check_and_create_tables(conn)

    except mysql.connector.Error as e:
        if e.errno == Error.ER_ACCESS_DENIED_ERROR:
            st.error("Error: Invalid database credentials. Please check your username and password.")
        else:
            st.error(f"Error connecting to the database: {e}")
        conn = None

    return conn

# Function to check if tables exist, and create them if not
def check_and_create_tables(conn):
    try:
        cursor = conn.cursor()

        # Check if 'books' table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'books'")
        if not cursor.fetchone():
            create_books_table(cursor)

        # Check if 'users' table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            create_users_table(cursor)

        # Check if 'carts' table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'carts'")
        if not cursor.fetchone():
            create_carts_table(cursor)

        cursor.close()

    except mysql.connector.Error:
        pass  # Ignore errors, e.g., if the user doesn't have permission to show tables

# Function to create 'books' table
def create_books_table(cursor):
    cursor.execute("""
        CREATE TABLE books (
            BookID INT AUTO_INCREMENT PRIMARY KEY,
            Title VARCHAR(255) NOT NULL,
            Author VARCHAR(255) NOT NULL,
            Price DECIMAL(10, 2) NOT NULL,
            Quantity INT NOT NULL
        )
    """)
    st.success("Table 'books' created successfully.")

# Function to create 'users' table
def create_users_table(cursor):
    cursor.execute("""
        CREATE TABLE users (
            UserID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(50) NOT NULL,
            Password VARCHAR(255) NOT NULL
        )
    """)
    st.success("Table 'users' created successfully.")

# Function to create 'carts' table
def create_carts_table(cursor):
    cursor.execute("""
        CREATE TABLE carts (
            CartID INT AUTO_INCREMENT PRIMARY KEY,
            UserID INT NOT NULL,
            BookID INT NOT NULL,
            Quantity INT NOT NULL
        )
    """)
    st.success("Table 'carts' created successfully.")

# Function to insert data from XML into the database
def insert_data():
    conn = connect_to_database()
    cursor = conn.cursor()

    # Parse and insert data from Books.xml
    insert_data_from_xml(conn, cursor, 'Books.xml', 'Books')

    # Parse and insert data from Users.xml
    insert_data_from_xml(conn, cursor, 'Users.xml', 'Users')

    # Parse and insert data from Carts.xml
    insert_data_from_xml(conn, cursor, 'Carts.xml', 'Carts')

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

# Function to insert data from XML into the specified table
def insert_data_from_xml(conn, cursor, xml_file_path, table_name):
    # Parse the XML file
    xml_tree = ET.parse(xml_file_path)
    xml_root = xml_tree.getroot()

    # Iterate over the child elements of the root element
    for child_element in xml_root.findall(f'.//{table_name}/row'):
        data = {}
        for sub_child_element in child_element:
            data[sub_child_element.tag] = sub_child_element.text

        # Insert data into the database
        columns = ', '.join(data.keys())
        values = ', '.join(["%s"] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        cursor.execute(query, tuple(data.values()))

# Function to view all tables
def view_all_tables():
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    # Display or return the data as needed
    st.write("Books:")
    st.write(books)

    # Repeat for other tables

    cursor.close()
    conn.close()

# Function to update a book
def update_book():
    conn = connect_to_database()
    cursor = conn.cursor()

    book_id = st.number_input("Enter Book ID to update:", min_value=1)
    new_quantity = st.number_input("Enter new quantity:", min_value=0)

    query = "UPDATE books SET Quantity = %s WHERE BookID = %s"
    cursor.execute(query, (new_quantity, book_id))

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    # Display updated information
    st.success(f"Quantity for BookID {book_id} updated to {new_quantity}.")

# Function to delete a cart entry
def delete_cart_entry():
    conn = connect_to_database()
    cursor = conn.cursor()

    cart_id = st.number_input("Enter Cart ID to delete:", min_value=1)

    query = "DELETE FROM carts WHERE CartID = %s"
    cursor.execute(query, (cart_id,))

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    # Display success message
    st.success(f"Cart entry with CartID {cart_id} deleted.")

def main():
    st.title("Online Bookstore")

    menu_options = ["Insert data", "View all tables", "Update", "Delete"]
    choice = st.sidebar.selectbox("Select an option", menu_options)

    if choice == "Insert data":
        insert_data()
    elif choice == "View all tables":
        view_all_tables()
    elif choice == "Update":
        update_book()
    elif choice == "Delete":
        delete_cart_entry()

if __name__ == "__main__":
    main()
