import mysql.connector

try:
    connection = mysql.connector.connect(
        unix_socket="/tmp/mysql.sock",  
        user="root",
        password="your_password",
        database="your_database"
    )
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    
    print(" Connected to database. Tables available:")
    for table in tables:
        print(table[0])

except mysql.connector.Error as err:
    print(f" Database connection failed: {err}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("🔌 Connection closed.")
