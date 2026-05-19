from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

import git_reader
import db
import os
import logging
load_dotenv()

def logging_init():
        logpath = Path("log")
        logpath.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
            handlers=[
        logging.FileHandler(logpath / "app.log", encoding="utf-8"),
        logging.StreamHandler(),   # 这个负责终端输出
    ]
    )

#检查并获取Path变量
def check_get_path(repo_path : str)->Path:
    if not repo_path:
        raise ValueError("请检查.env文件，repo_path没有内容,或无次环境变量")
    else:
        return git_reader.check_path(repo_path)


#获取git日志和diff并保存为markdown
def process_git_report(path:Path,time):
    if git_reader.check_git(path):
        logging.info("此路径是git仓库---准备进行日志检查，diff差别并保存文件")
        logging.debug("创建reports_dir变量，此变量为reports路径")
        reports_dir = path/"reports"
        logging.info("检查目录下reports文件夹是否存在，存在创建不存在跳过")
        reports_dir.mkdir(exist_ok=True)
        logging.debug("创建report_path变量，此变量为markdown文件路径")
        report_path = reports_dir / f"{time}.md"
        reports = git_reader.generate_report(path)
        report_path.write_text(reports,encoding="utf-8")
        logging.info("完成日志查询和diff差别并存入文件%s.md",time)
        log = git_reader.git_log(path)
        commit_count = len(log.splitlines()) if log.strip() else 0
        #数据库插入reports
        logging.info("进行数据库插入")
        row_id = db.insert_reports(report_date=time,commit_count=commit_count,report_content=reports)
        logging.info("数据库插入成功，id: %s", row_id)
        return row_id
    else:
        logging.warning("此路径不是git仓库")
        return

#调用deepseekapi进行日志分析
def log_analyse(path:Path,time,db_id:int):
    logging.info("---开始调用deepseek整理日志变化信息！请等待......---")
    stat = git_reader.git_stat(path)
    if not stat.strip():
        logging.info("---今日无日志提交记录，跳过ai整理---")
        return
    logging.debug("创建reports_dir变量，此变量为reports路径")
    reports_dir = path/"reports"
    deepseek_report = git_reader.analyze_with_deepseek(stat)
    Path(reports_dir/f"{time}deepseek分析.txt").write_text(deepseek_report,encoding="utf-8")
    logging.info("准备将分析存入数据库")
    db.update_report(id=db_id,value=deepseek_report)
    logging.info("数据库存储完成")
    logging.info("完成日志整理并存入%s",reports_dir/f"{time}deepseek分析.txt")
    return


#主程序
def main():
    logging_init()
    logging.info("程序启动")
    try:
        init_path = os.getenv("repo_path")
        path = check_get_path(init_path)
        datetime_now = datetime.now().strftime("%Y-%m-%d")
        logging.info("完成初始化路径检查")
        db_id = process_git_report(path=path,time=datetime_now)
        if db_id is None:
            logging.warning("未获取到db_id，跳过ai分析")
            return
        log_analyse(path=path,time=datetime_now,db_id=db_id)
        logging.info("程序运行完毕")
        return
    except ValueError as e:
        logging.error(e)
    except FileNotFoundError:
        logging.error("路径不存在，请检查 .env 中的 repo_path")
    except NotADirectoryError:
        logging.error("路径不是文件夹，请检查 .env 中的 repo_path")
    except Exception as e:
        logging.error("未知错误%s",e,exc_info=True)

if __name__ == "__main__":
    main()
