import os
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

from urllib.parse import urlparse, unquote

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL") or os.getenv("JAWSDB_URL") or os.getenv("CLEARDB_DATABASE_URL")

if DATABASE_URL:
    # Support mysql:// or mysql2:// or pymysql:// formats
    if DATABASE_URL.startswith("mysql2://") or DATABASE_URL.startswith("mysql+pymysql://"):
        cleaned_url = "mysql://" + DATABASE_URL.split("://", 1)[1]
    else:
        cleaned_url = DATABASE_URL
    parsed = urlparse(cleaned_url)
    DB_HOST = parsed.hostname or "localhost"
    DB_PORT = int(parsed.port or 3306)
    DB_USER = unquote(parsed.username or "root")
    DB_PASSWORD = unquote(parsed.password or "")
    DB_NAME = parsed.path.lstrip("/").split("?")[0] if parsed.path else "disaster_relief_db"
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "disaster_relief_db")

DB_SSL_ENABLED = (
    os.getenv("DB_SSL", "false").lower() in ("true", "1", "yes", "require")
    or "tidbcloud" in DB_HOST.lower()
    or "aivencloud" in DB_HOST.lower()
    or "railway" in DB_HOST.lower() and DB_PORT != 3306
)

def _get_connect_args(with_db=True):
    args = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True,
        "connect_timeout": 10
    }
    if with_db and DB_NAME:
        args["database"] = DB_NAME
    if DB_SSL_ENABLED:
        args["ssl"] = {"ssl": {}}
    return args

def get_server_connection():
    """Connect to MySQL server without selecting a database (for init/check)."""
    return pymysql.connect(**_get_connect_args(with_db=False))

def get_db_connection():
    """Connect to the specific disaster_relief_db database."""
    return pymysql.connect(**_get_connect_args(with_db=True))

def check_connection():
    """Check if MySQL connection is operational."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS status")
            result = cursor.fetchone()
        conn.close()
        return True, "Connected to MySQL successfully"
    except Exception as e:
        try:
            # Check if server is alive even if DB is not created yet
            conn = get_server_connection()
            conn.close()
            return True, f"Connected to MySQL server (Database '{DB_NAME}' not yet initialized)"
        except Exception as e2:
            return False, str(e2)

def init_db():
    """Execute schema.sql to create database and tables."""
    try:
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        # Connect to MySQL server and create database if not exists
        server_conn = get_server_connection()
        with server_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        server_conn.close()

        # Connect to DB and run schema statements
        conn = get_db_connection()
        with conn.cursor() as cursor:
            statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
            for stmt in statements:
                # Skip USE statements as we are already connected to the database
                if stmt.upper().startswith("USE ") or stmt.upper().startswith("CREATE DATABASE"):
                    continue
                cursor.execute(stmt)
        conn.close()
        return True, "Database schema initialized successfully."
    except Exception as e:
        return False, f"Failed to initialize schema: {e}"

def seed_db():
    """Seed the database with default sample data from seed.sql."""
    try:
        # First ensure schema exists
        init_ok, init_msg = init_db()
        if not init_ok:
            return False, init_msg

        seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
        with open(seed_path, "r", encoding="utf-8") as f:
            sql_content = f.read()

        conn = get_db_connection()
        with conn.cursor() as cursor:
            statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
            for stmt in statements:
                if stmt.upper().startswith("USE "):
                    continue
                cursor.execute(stmt)
        conn.close()
        return True, "Database seeded with sample records successfully."
    except Exception as e:
        return False, f"Failed to seed data: {e}"

def execute_query(query, params=None):
    """Execute SELECT query and return list of dictionaries."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

def execute_one(query, params=None):
    """Execute SELECT query and return single row dictionary."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        conn.close()

def execute_update(query, params=None):
    """Execute INSERT, UPDATE, DELETE queries and return affected rows."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            affected = cursor.execute(query, params or ())
            return affected
    finally:
        conn.close()

def run_raw_sql(sql_code):
    """Execute raw SQL statements entered by the user and return results/columns or affected rows."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            statements = [s.strip() for s in sql_code.split(";") if s.strip()]
            all_results = []
            for stmt in statements:
                if stmt.upper().startswith("USE "):
                    continue
                cursor.execute(stmt)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    all_results.append({
                        "query": stmt,
                        "type": "SELECT",
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows)
                    })
                else:
                    all_results.append({
                        "query": stmt,
                        "type": "DML/DDL",
                        "affected_rows": cursor.rowcount,
                        "message": f"Query OK, {cursor.rowcount} row(s) affected"
                    })
            return True, all_results
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
