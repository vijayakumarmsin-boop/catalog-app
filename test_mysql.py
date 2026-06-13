from mysql_db import conn

if conn.is_connected():
    print("Connection Success")
else:
    print("Connection Failed")