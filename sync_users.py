import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="catalog123",
    database="catalogue_db"
)

cursor = conn.cursor()

# ADD USER
cursor.execute(
    "INSERT INTO users (username, password) VALUES (%s, %s)",
    ("viji", "123456")
)

conn.commit()

# FETCH LATEST USERS
query = "SELECT * FROM users"
df = pd.read_sql(query, conn)

# AUTO UPDATE EXCEL
df.to_excel("users.xlsx", index=False)

print("Excel Updated")