import streamlit as st
import mysql.connector
import pandas as pd

class Database:
    def __init__(self, host, user, password, port, database):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = database
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host, user=self.user, password=self.password, port=self.port, database=self.database)
        self.cursor = self.conn.cursor()
        st.success("Connection successful")
    
    def execute_query(self, query):
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description] 
        result = self.cursor.fetchall()
        return pd.DataFrame(result, columns=columns) 
    
    def execute_commit(self, query):
        self.cursor.execute(query)
        self.conn.commit()

config = {
    "host": "gateway01.ap-southeast-1.prod.aws.tidbcloud.com", 
    "user": "2Sq2DQiR5GcBS1k.root", 
    "port": 4000, 
    "password": "AoyZ0L33qUgeKtFp", 
    "database": "Zomato"
}

db_obj = Database(**config)
db_obj.connect()

# Streamlit App
st.title("MySQL Database Manager")

task = st.sidebar.selectbox("Select Operation", ["View Tables", "Create Table","Insert Record", "Read Records", "Update Record", "Delete Record", "Run SQL Query"])

if task == "View Tables":
    db_obj.cursor.execute("SHOW TABLES")
    tables = db_obj.cursor.fetchall()
    st.write("Tables in Database:")
    st.write(pd.DataFrame(tables, columns=["Tables"]))

elif task == "Create Table":
    table_name = st.text_input("Enter Table Name")
    num_columns = st.number_input("Number of Columns", min_value=1, step=1, value=1)
    columns = []
    for i in range(num_columns):
     col_name = st.text_input(f"Column {i+1} Name")
     col_type = st.selectbox(f"Column {i+1} Data Type", ["INT", "VARCHAR(255)", "TEXT", "DATE", "FLOAT", "BOOLEAN", "DATETIME"], key=f"type_{i}")
     col_constraints = st.text_input(f"Column {i+1} Constraints (e.g., PRIMARY KEY, NOT NULL, AUTO_INCREMENT)", key=f"const_{i}")
     columns.append((col_name, col_type, col_constraints))

    if st.button("Create Table"):
        column_definitions = ", ".join([f"{name} {dtype} {constraints}".strip() for name, dtype, constraints in columns if name])
        query = f"CREATE TABLE {table_name} ({column_definitions})"
        db_obj.cursor.execute(query)
        db_obj.conn.commit()
        st.success(f"Table '{table_name}' created successfully!") 

elif task == "Insert Record":
    table_name = st.text_input("Enter Table Name")
    if table_name:
        db_obj.cursor.execute(f"DESCRIBE {table_name}")
        columns = [col[0] for col in db_obj.cursor.fetchall()]
        values = {col: st.text_input(f"Enter value for {col}", key=f"value_{col}") for col in columns}
    if st.button("Insert Record"):
                col_names = ", ".join(values.keys())
                col_values = ", ".join(f"'{val}'" for val in values.values())
                query = f"INSERT INTO {table_name} ({col_names}) VALUES ({col_values})"
                db_obj.execute_commit(query)
                st.success(f"Record inserted successfully into '{table_name}'!")              
        
elif task == "Read Records":
    table_name = st.text_input("Enter Table Name")
    if st.button("Fetch Records"):
        query = f"SELECT * FROM {table_name}"
        result_df = db_obj.execute_query(query)
        st.write(result_df)

elif task == "Update Record":
    table_name = st.text_input("Enter Table Name")
    set_clause = st.text_input("Enter SET Clause (e.g., column=value)")
    condition = st.text_input("Enter WHERE Condition")
    if st.button("Update Record"):
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        db_obj.execute_commit(query)
        st.success("Record Updated Successfully")

elif task == "Delete Record":
    table_name = st.text_input("Enter Table Name")
    condition = st.text_input("Enter WHERE Condition")
    if st.button("Delete Record"):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        db_obj.execute_commit(query)
        st.success("Record Deleted Successfully")

elif task == "Run SQL Query":
    query = st.text_area("Enter SQL Query")
    if st.button("Run Query"):
        result_df = db_obj.execute_query(query)
        st.write(result_df)

# 20 SQL Queries for Order, Customer, Delivery, and Restaurant Insights
sql_queries = {
    "Busy Ordering Hours": "SELECT HOUR(order_date) AS Peak_hour, COUNT(*) AS order_count FROM Orders GROUP BY HOUR(order_date) ORDER BY order_count DESC LIMIT 20;",
    "Top Ordering Locations": "SELECT location, COUNT(*) AS order_count FROM Customers JOIN Orders ON Customers.customer_id = Orders.customer_id GROUP BY location ORDER BY order_count DESC;",
    "Delayed Deliveries": "SELECT order_id, (delivery_time - estimated_time) AS delay FROM Deliveries WHERE delivery_time > estimated_time;",
    "Cancelled Orders": "SELECT COUNT(*) AS cancelled_orders FROM Orders WHERE status = 'Cancelled';",
    "Customer with Most Orders": "SELECT customer_id, COUNT(*) AS order_count FROM Orders GROUP BY customer_id ORDER BY order_count DESC LIMIT 50;",
    "Top 10 Customers": "SELECT customer_id, SUM(total_amount) AS total_spent FROM Orders GROUP BY customer_id ORDER BY total_spent DESC LIMIT 10;",
    "Average Delivery Time": "SELECT AVG(delivery_time) AS avg_delivery_time FROM Deliveries;",
    "Best Delivery Personnels": "SELECT delivery_person_id, AVG(average_rating) AS avg_rating FROM DeliveryPersons GROUP BY delivery_person_id ORDER BY avg_rating DESC LIMIT 10;",
    "Most Popular Restaurants": "SELECT restaurant_id, COUNT(*) AS order_count FROM Orders GROUP BY restaurant_id ORDER BY order_count DESC;",
    "Most Popular Cuisines": "SELECT cuisine_type, COUNT(*) AS order_count FROM Restaurants JOIN Orders ON Restaurants.restaurant_id = Orders.restaurant_id GROUP BY cuisine_type ORDER BY order_count DESC;",
    "Average Order Value": "SELECT AVG(total_amount) AS avg_order_value FROM Orders;",
    "Total Revenue per Restaurant": "SELECT restaurant_id, SUM(total_amount) AS total_revenue FROM Orders GROUP BY restaurant_id;",
    "Frequent Order Status": "SELECT status, COUNT(*) AS status_count FROM Orders GROUP BY status ORDER BY status_count DESC;",
    "Total Deliveries per Delivery Person": "SELECT delivery_person_id, COUNT(*) AS deliveries_count FROM Deliveries GROUP BY delivery_person_id;",
    "Highest Delivery Fee": "SELECT MAX(delivery_fee) AS max_delivery_fee FROM Deliveries;",
    "Total Revenue from Premium Customers": "SELECT SUM(total_amount) AS Premium_revenue FROM Orders JOIN Customers ON Orders.customer_id = Customers.customer_id WHERE Customers.is_premium = TRUE;",
    "Restaurant with Highest Ratings": "SELECT restaurant_id, AVG(rating) AS avg_rating FROM Restaurants GROUP BY restaurant_id ORDER BY avg_rating DESC;",
    "Most Frequent Payment Mode": "SELECT payment_mode, COUNT(*) AS usage_count FROM Orders GROUP BY payment_mode ORDER BY usage_count DESC LIMIT 2;",
    "Top 5 Restaurants by Rating" :"SELECT name AS restaurant_name, rating, total_orders FROM Restaurants ORDER BY rating DESC, total_orders DESC LIMIT 5;",
    "Top 5 Customers by Orders": "SELECT customer_id, name, total_orders FROM Customers ORDER BY total_orders DESC LIMIT 5;"

}

st.subheader("Run Predefined Queries")
query_choice = st.selectbox("Select a Query", list(sql_queries.keys()))
if st.button("Run Selected Query"):
    result_df = db_obj.execute_query(sql_queries[query_choice])
    st.write(result_df)
