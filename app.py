import streamlit as st
import mysql.connector
import xml.etree.ElementTree as ET

# Function to view all tables
def view_all_tables():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="my_database"
    )

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
    book_id = st.number_input("Enter Book ID to update:", min_value=1)
    new_quantity = st.number_input("Enter new quantity:", min_value=0)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="my_database"
    )

    cursor = conn.cursor()
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
    cart_id = st.number_input("Enter Cart ID to delete:", min_value=1)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="my_database"
    )

    cursor = conn.cursor()
    query = "DELETE FROM carts WHERE CartID = %s"
    cursor.execute(query, (cart_id,))

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    # Display success message
    st.success(f"Cart entry with CartID {cart_id} deleted.")

# Streamlit app
def main():
    st.title("Online Bookstore")

    menu_options = ["Insert data", "View all tables", "Update", "Delete"]
    choice = st.sidebar.selectbox("Select an option", menu_options)

    if choice == "Insert data":
        # Implement the logic to insert data
        pass
    elif choice == "View all tables":
        view_all_tables()
    elif choice == "Update":
        update_book()
    elif choice == "Delete":
        delete_cart_entry()

if __name__ == "__main__":
    main()
