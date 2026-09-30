import pyodbc
from config.settings import build_connection_string


def main():
    connection_string = build_connection_string()

    with pyodbc.connect(connection_string, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT @@SERVERNAME, DB_NAME()")
        server_name, database_name = cursor.fetchone()

    print("=== SQL CONNECTION CHECK ===")
    print(f"Server:   {server_name}")
    print(f"Database: {database_name}")
    print("SQL connection PASSED.")


if __name__ == "__main__":
    main()
