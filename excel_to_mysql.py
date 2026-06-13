import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="catalog123",
    database="catalogue_db"
)

cursor = conn.cursor()

df = pd.read_excel("products.xlsx")

df = df.fillna("")

print(df.head())

for _, row in df.iterrows():

  values = (
    str(row.get("product", "")),
    str(row.get("brand", "")),
    str(row.get("category", "")),
    float(str(row.get("price", 0)).replace(",", "").replace("₹", "")),
    float(str(row.get("mrp", 0)).replace(",", "").replace("₹", "")),
    str(row.get("description", "")),
    str(row.get("Image URL", ""))
)
cursor.execute("""
        INSERT INTO products
        (product_name, brand, category, price, mrp, description, image_path)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, values)

conn.commit()

print("DONE")