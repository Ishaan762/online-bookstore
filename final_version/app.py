import streamlit as st
import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET

# Define a SessionState class to persist the connection state
class SessionState:
    def __init__(self):
        self.conn = None
        self.data_inserted = False

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

        return conn

    except mysql.connector.Error as e:
        if e.errno == Error.ER_ACCESS_DENIED_ERROR:
            st.error("Error: Invalid database credentials. Please check your username and password.")
        else:
            st.error(f"Error connecting to the database: {e}")

    return None

# Function to check if tables exist, and create them if not
def check_and_create_tables(conn):
    try:
        cursor = conn.cursor()

        # Check if 'books' table exists
        cursor.execute("SHOW TABLES LIKE 'books'")
        if not cursor.fetchone():
            create_books_table(cursor)

        # Check if 'users' table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            create_users_table(cursor)

        # Check if 'carts' table exists
        cursor.execute("SHOW TABLES LIKE 'carts'")
        if not cursor.fetchone():
            create_carts_table(cursor)

        cursor.close()

    except mysql.connector.Error as e:
        st.error(f"Error checking and creating tables: {e}")

# Function to create 'books' table
def create_books_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            BookID INT PRIMARY KEY,
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
        CREATE TABLE IF NOT EXISTS users (
            UserID INT PRIMARY KEY,
            Username VARCHAR(50) NOT NULL,
            Password VARCHAR(255) NOT NULL
        )
    """)
    st.success("Table 'users' created successfully.")

# Function to create 'carts' table
def create_carts_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            CartID INT PRIMARY KEY,
            UserID INT NOT NULL,
            BookID INT NOT NULL,
            Quantity INT NOT NULL
        )
    """)
    st.success("Table 'carts' created successfully.")


def populate_database(conn, xml_file_path):
    cursor = conn.cursor()

    # Parse the XML file
    xml_tree = ET.parse(xml_file_path)
    xml_root = xml_tree.getroot()

    for table in xml_root:
        table_name = table.tag
        for row in table:
            data = {}
            for attr in row:
                data[attr.tag] = attr.text

            columns = ', '.join(data.keys())
            values = ', '.join(["%s"] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

            try:
                cursor.execute(query, tuple(data.values()))
                st.success(f"Data inserted into {table_name} successfully.")
            except mysql.connector.Error as e:
                st.error(f"Error inserting data into {table_name}: {e}")

    # Commit the changes
    conn.commit()
    cursor.close()



def insert_data(conn, session_state):
    if conn is None:
        conn = connect_to_database()
    if not session_state.data_inserted:
        if st.button("Confirm Insert Operation"):
            # Call the populate_database function instead of the previous insert_data_from_xml
            populate_database(conn, 'initial_data.xml')

            # Set the flag to indicate that data has been inserted
            session_state.data_inserted = True

            st.success("Data inserted successfully.")
            

            # Print debug information
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books")
            st.write("Books table after insert:")
            st.table(cursor.fetchall())
            cursor.close()

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            st.write("Users table after insert:")
            st.table(cursor.fetchall())
            cursor.close()

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM carts")
            st.write("Carts table after insert:")
            st.table(cursor.fetchall())
            cursor.close()
    else:
        st.info("Data has already been inserted. To insert again, please restart the app.")
	
    conn.commit()


# Function to view all tables
def view_all_tables(conn):
    cursor = conn.cursor(dictionary=True)

    # Get all table names in the database
    cursor.execute("SHOW TABLES")
    tables = [table['Tables_in_my_database'] for table in cursor.fetchall()]

    # Print intermediate result
    print("Tables:", tables)

    # Display data for all tables
    for table_name in tables:
        st.write(f"{table_name.capitalize()}:")
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        st.table(data)

    cursor.close()

def update_book(conn, xml_file_path):
    cursor = conn.cursor()

    # Parse the XML file
    xml_tree = ET.parse(xml_file_path)
    xml_root = xml_tree.getroot()

    for child_element in xml_root.findall('.//Books/row'):
        book_id = child_element.find('BookID').text
        new_title = child_element.find('Title').text
        new_author = child_element.find('Author').text
        new_price = child_element.find('Price').text
        new_quantity = child_element.find('Quantity').text

        st.write(f"BookID: {book_id}")
        st.write(f"New Title: {new_title}")
        st.write(f"New Author: {new_author}")
        st.write(f"New Price: {new_price}")
        st.write(f"New Quantity: {new_quantity}")

        # Add a confirmation button before executing the update
        if st.button("Confirm Update"):
            query = "UPDATE books SET Title = %s, Author = %s, Price = %s, Quantity = %s WHERE BookID = %s"
            cursor.execute(query, (new_title, new_author, new_price, new_quantity, book_id))

            # Commit the changes
            conn.commit()

            st.success("Book updated successfully.")

    cursor.close()

def delete_cart_entry(conn):
    cursor = conn.cursor()

    cart_id = st.number_input("Enter Cart ID to delete:", min_value=1)

    # Display a confirmation button before executing the delete
    if st.button("Confirm Delete"):
        query = "DELETE FROM carts WHERE CartID = %s"
        cursor.execute(query, (cart_id,))

        # Commit the changes
        conn.commit()
        
        st.success(f"Cart entry with CartID {cart_id} deleted.")

    cursor.close()



# Streamlit app
def main():
    st.set_page_config(page_title="Online Bookstore", page_icon="📚")
    st.title("Online Bookstore")

    # Initialize or retrieve session state
    session_state = SessionState()

    if not session_state.conn:
        # If connection is not established, connect to the database
        session_state.conn = connect_to_database()

    if session_state.conn:
        menu_options = ["Insert data", "View all tables", "Update", "Delete"]
        choice = st.selectbox("Select an option", menu_options)

        if choice == "Insert data":
            insert_data(session_state.conn, session_state)
        elif choice == "View all tables":
            view_all_tables(session_state.conn)
        elif choice == "Update":
            update_book(session_state.conn, 'update_data.xml')
        elif choice == "Delete":
            delete_cart_entry(session_state.conn)

    # Close the connection when the Streamlit app is closed
    if session_state.conn:
        session_state.conn.close()

if __name__ == "__main__":
    main()
