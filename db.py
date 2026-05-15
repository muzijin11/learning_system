import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def test_connection():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL 版本: {version[0]}")
    cursor.close()
    conn.close()

def insert_report(report_date: str, commit_count: int, report_content: str, ai_analysis: str):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO daily_reports (report_date, commit_count, report_content, ai_analysis)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (report_date, commit_count, report_content, ai_analysis))
    conn.commit()
    cursor.close()
    conn.close()
    return cursor.lastrowid


if __name__ == "__main__":
    test_connection()
    row_id = insert_report(
        report_date="2026-05-14",
        commit_count=3,
        report_content="# 今日开发报告",
        ai_analysis="今日完成 logging 模块"
    )
    print(f"---{row_id}---")