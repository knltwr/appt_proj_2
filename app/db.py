import psycopg2
# Connect to your postgres DB
try:
    conn = psycopg2.connect(database="appt_proj_2", user="postgres", password="password", host="localhost", port=5432)
    print("success")
except Exception as e:
    print(e)

# # Open a cursor to perform database operations
# cur = conn.cursor()

# # Execute a query
# cur.execute("SELECT * FROM my_data")

# # Retrieve query results
# records = cur.fetchall()
