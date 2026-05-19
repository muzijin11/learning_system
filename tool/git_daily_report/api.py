from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from datetime import date
from mysql.connector import Error as DBError
from dotenv import load_dotenv
import logging
import db

load_dotenv()

app = FastAPI()

class ReportOut(BaseModel):
    id : int
    report_date:date
    commit_count:int
    report_content:str | None = None
    ai_analysis:str | None = None



@app.get("/reports",response_model=list[ReportOut])
def get_reports():
    try:
        return db.select_all_reports()
    except DBError as e:
        logging.error("数据库错误: %s", e)
        raise HTTPException(status_code=500,detail="数据库错误，请稍后重试")
    

@app.get("/reports/latest",response_model=ReportOut)
def get_report_latest():
    try:
        result = db.select_latest()
        if not result:
            raise HTTPException(status_code=404,detail="查不到数据")
        return result
    except DBError as e:
        logging.error("数据库错误: %s", e)
        raise HTTPException(status_code=500,detail="数据库错误，请稍后重试")



@app.get("/reports/{date}",response_model=ReportOut)
def get_report(date:str):
    try:
        result = db.select_report(date) 
        if not result:
            raise HTTPException(status_code=404,detail=f"{date}无日志内容")
        return result
    except DBError as e:
        logging.error("数据库错误: %s", e)
        raise HTTPException(status_code=500,detail="数据库错误，请稍后重试")