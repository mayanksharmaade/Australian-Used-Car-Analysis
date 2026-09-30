import pyodbc

# Change this to the same server name you use in SSMS
SERVER = r"DESKTOP-NEE3MSU\SQLEXPRESS"
DATABASE = "AustralianUsedCarAnalytics"

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

try:
    print("Connecting to SQL Server...")

    connection = pyodbc.connect(connection_string)

    cursor = connection.cursor()

    cursor.execute("SELECT DB_NAME();")
    database_name = cursor.fetchone()[0]

    cursor.execute("SELECT @@SERVERNAME;")
    server_name = cursor.fetchone()[0]

    print("Connection successful!")
    print("Server:", server_name)
    print("Database:", database_name)

    cursor.close()
    connection.close()

except Exception as error:
    print("Connection failed.")
    print(error)