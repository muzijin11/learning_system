import mysql.connector
import os
import logging

def connect_db():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except Exception as e:
        logging.error(f"连接数据库失败：{e}")
        return None



def insert_reports(report_date:str,commit_count:int=0,report_content:str=None,ai_analysis:str=None):
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                sql = """insert into daily_reports (report_date,commit_count,report_content,ai_analysis) values(%s,%s,%s,%s)"""
                cursor.execute(sql,(report_date,commit_count,report_content,ai_analysis))
                conn.commit()
                return cursor.lastrowid
    except Exception as e:
        logging.error(f"insert失败:{e}")
        return None

def update_report(id:int,value:str):
    try:
        with connect_db() as conn:
            with conn.cursor() as cursor:
                sql = """update daily_reports set ai_analysis = %s where id = %s"""
                cursor.execute(sql,(value,id))
                conn.commit()
                return
    except Exception as e:
        logging.error(f"update失败：{e}")
        return None

def select_all_reports():
        try:
            with connect_db() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    sql = """select * from daily_reports"""
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    return result
        except Exception as e:
            logging.error(f"select all失败：{e}")
            return None
        

def select_report(date:str):
    try:
        with connect_db() as conn:
            with conn.cursor(dictionary=True,buffered=True) as cursor:
                sql = """select * from daily_reports where report_date = %s"""
                cursor.execute(sql,(date,))
                result = cursor.fetchone()
                return result
    except Exception as e:
        logging.error(f"select date失败：{e}")
        return None


def select_latest():
    try:
        with connect_db() as conn:
            with conn.cursor(dictionary=True,buffered=True) as cursor:
                sql = """select * from daily_reports order by id desc limit 1"""
                cursor.execute(sql)
                result = cursor.fetchone()
                return result
    except Exception as e:
        logging.error(f"select latest失败：{e}")
        return None

