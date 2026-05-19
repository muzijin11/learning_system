import mysql.connector
import os

def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def insert_reports(report_date:str,commit_count:int=0,report_content:str=None,ai_analysis:str=None):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            sql = """insert into daily_reports (report_date,commit_count,report_content,ai_analysis) values(%s,%s,%s,%s)"""
            cursor.execute(sql,(report_date,commit_count,report_content,ai_analysis))
            conn.commit()
            return cursor.lastrowid
        

def update_report(id:int,value:str):
    with connect_db() as conn:
        with conn.cursor() as cursor:
            sql = """update daily_reports set ai_analysis = %s where id = %s"""
            cursor.execute(sql,(value,id))
            conn.commit()
            return
        
def select_all_reports():
    with connect_db() as conn:
        with conn.cursor(dictionary=True) as cursor:
            sql = """select * from daily_reports"""
            cursor.execute(sql)
            result = cursor.fetchall()
            return result


def select_report(date:str):
    with connect_db() as conn:
        with conn.cursor(dictionary=True,buffered=True) as cursor:
            sql = """select * from daily_reports where report_date = %s"""
            cursor.execute(sql,(date,))
            result = cursor.fetchone()
            return result


def select_latest():
    with connect_db() as conn:
        with conn.cursor(dictionary=True,buffered=True) as cursor:
            sql = """select * from daily_reports order by id desc limit 1"""
            cursor.execute(sql)
            result = cursor.fetchone()
            return result


