from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

import git_reader
import os
load_dotenv()



if __name__ == "__main__":

    try:
        file_path = os.getenv("repo_path")
        if not file_path:
            print("路径为空请检查.env文件")
        else:
            file_path = git_reader.check_path(file_path)
            
            datetime_now = datetime.now().strftime("%Y-%m-%d")
            if git_reader.check_git(file_path):
                print("此路径是git仓库\n即将执行检查日志操作------")
                print(git_reader.git_log(file_path))

                print("完成日志检查---------\n准备执行diff查询区别")
                print(git_reader.git_diff(file_path))

                print("完成diff查询---------\n准备创建markdown文件并写入日志")
                reports_dir = file_path/Path("reports")
                reports_dir.mkdir(exist_ok=True)
                report_path = reports_dir / f"{datetime_now}.md"
                report_path.write_text(git_reader.generate_report(file_path),encoding="utf-8")
                print(f"已添加{report_path}格式的git日志记录")

                print("---开始调用deepseek整理日志变化信息！请等待......---")
                stat = git_reader.git_stat(file_path)
                if not stat.strip():
                    print("---今日无日志提交记录，跳过ai整理---")
                else:
                    deepseek_report = git_reader.deepseekapi(stat)
                    Path(reports_dir/f"{datetime_now}deepseek分析.txt").write_text(deepseek_report,encoding="utf-8")
                    print(deepseek_report)
                
            else:
                print("此路径不为git仓库")
    except FileNotFoundError:
        print("这个路径不存在！")
    except NotADirectoryError:
        print("这个路径不是一个文件夹！")


