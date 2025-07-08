import os
import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=os.getenv("MYSQL_PORT"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )

def log_build_to_db(workflow_name, run_id, status, conclusion, triggered_by):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO build_history 
            (workflow_name, run_id, status, conclusion, triggered_by, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            workflow_name,
            run_id,
            status,
            conclusion,
            triggered_by,
            datetime.now()
        )
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        print("Build logged in DB")
    except Exception as e:
        print("DB logging failed:", e)

def get_all_builds():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM build_history ORDER BY timestamp DESC")
        builds = cursor.fetchall()
        cursor.close()
        conn.close()
        return builds
    except Exception as e:
        print("Failed to retrieve builds:", e)
        return []

