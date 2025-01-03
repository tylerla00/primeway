import psycopg2
from psycopg2 import sql

# Replace with your database connection details
conn = psycopg2.connect(
    dbname="primeway_db",
    user="user",
    password="password",
    host="localhost",
    port="5432"  # Default PostgreSQL port
)

# Create a cursor object
cur = conn.cursor()

# Sample query to fetch data
cur.execute("SELECT * FROM user_tokens;")

# Fetch all rows
rows = cur.fetchall()

# Print rows
for row in rows:
    print(row)

# Close the cursor and connection
cur.close()
conn.close()