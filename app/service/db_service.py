import json
import psycopg2
import psycopg2.extras  
from typing import Optional, Dict, Any  
import re
from app.core.config import settings


FORBIDDEN_TABLES = ["user", "user_role", "role"]

def _find_forbidden_tables(query: str) -> Optional[str]:
    """Checks if the query attempts to access forbidden tables."""
    lower_query = query.lower()
    for table in FORBIDDEN_TABLES:
        pattern = rf"(?:from|join|update|into)\s+[\w.\"\[\]]*{re.escape(table)}\b"
        if re.search(pattern, lower_query):
            return table
        # Check specifically for DELETE FROM table pattern
        delete_pattern = rf"delete\s+from\s+[\w.\"\[\]]*{re.escape(table)}\b"
        if re.search(delete_pattern, lower_query):
            return table
    return None


def query_database(sql_query: str) -> str:
    """Executes a given SQL query against the PostgreSQL database (synchronous) and returns results as JSON.

    Connects to the database using credentials from the application settings.
    Executes the provided SQL query safely, preventing access to forbidden tables
    ('user', 'user_role', 'role').

    Handles SELECT queries by returning fetched data and modification queries
    (INSERT, UPDATE, DELETE) by returning the number of affected rows.

    Args:
        sql_query: The raw SQL query string to execute.
            Example SELECT: "SELECT id, name FROM products WHERE category = 'electronics' LIMIT 10;"
            Example INSERT: "INSERT INTO orders (customer_id, order_date) VALUES (123, NOW());"
                         (Note: ensure target table is not forbidden)

    Returns:
        A JSON string representing the query result or an error.
        On successful SELECT: '{"data": [{"col1": val1, ...}, ...]}'
        On successful INSERT/UPDATE/DELETE: '{"status": "success", "rows_affected": count}'
        On forbidden query attempt: '{"error": "Forbidden Query", "message": "Access to table '...' is restricted."}'
        On database or other errors: '{"error": "Error Type", "message": "Error details..."}'
        Example Failure (Forbidden): '{"error": "Forbidden Query", "message": "Access to table 'user' is restricted."}'
        Example Failure (DB Error): '{"error": "Database Error", "message": "relation \\"productss\\" does not exist"}'
        Example Success (SELECT): '{"data": [{"id": 1, "name": "Laptop"}, {"id": 2, "name": "Mouse"}]}'
        Example Success (INSERT): '{"status": "success", "rows_affected": 1}'
    """
    conn = None
    cursor = None
    result_payload: Dict[str, Any] = {}

    # 1. Input Validation / Security Check
    if not isinstance(sql_query, str) or not sql_query.strip():
        result_payload = {
            "error": "Invalid Input",
            "message": "SQL query cannot be empty.",
        }
        return json.dumps(result_payload)

    forbidden_table = _find_forbidden_tables(sql_query)
    if forbidden_table:
        result_payload = {
            "error": "Forbidden Query",
            "message": f"Access to table '{forbidden_table}' is restricted.",
        }
        return json.dumps(result_payload)

    is_select_query = sql_query.strip().lower().startswith("select")

    try:
        # 2. Establish Database Connection
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            # Using DictCursor to get results as dictionaries
            cursor_factory=psycopg2.extras.DictCursor,
        )
        # Set autocommit to False to manage transactions explicitly
        conn.autocommit = False

        # 3. Create Cursor and Execute Query
        cursor = conn.cursor()
        cursor.execute(sql_query)

        # 4. Process Results
        if is_select_query and cursor.description:

            rows = cursor.fetchall()

            result_payload = {"data": [dict(row) for row in rows]}
        else:

            rows_affected = cursor.rowcount
            result_payload = {"status": "success", "rows_affected": rows_affected}

            conn.commit()  

    # 5. Handle Potential Errors
    except psycopg2.Error as db_err:

        if conn:
            conn.rollback()  
        error_type = type(db_err).__name__  
        error_message = str(db_err).split("\n")[0]  
        print(
            f"Database Error ({error_type}): {db_err.pgcode} - {db_err.pgerror}"
        )  
        result_payload = {
            "error": "Database Error",
            "message": error_message,
            "type": error_type,
        }
    except Exception as e:

        if conn:
            conn.rollback()
        error_type = type(e).__name__
        print(f"Unexpected Error during DB query: {e}")  
        result_payload = {
            "error": "Unexpected Error",
            "message": str(e),
            "type": error_type,
        }

    # 6. Cleanup: Close cursor and connection
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # 7. Serialize Result to JSON
    try:
        # Use default=str to handle potential non-serializable types like dates/decimals
        return json.dumps(result_payload, ensure_ascii=False, default=str)
    except TypeError as json_err:
        print(f"JSON Serialization Error: {json_err}")
        # Fallback error message if JSON serialization itself fails
        return json.dumps(
            {
                "error": "Serialization Error",
                "message": "Could not serialize query results to JSON.",
            }
        )


