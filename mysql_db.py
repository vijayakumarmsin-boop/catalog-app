import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="catalog123",
    database="catalogue_db"
)

query = "SELECT * FROM users"

df = pd.read_sql(query, conn)

print(df)