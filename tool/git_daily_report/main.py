import git_reader
from pathlib import Path
from datetime import datetime

try:
    file_path = git_reader.check_path(input("请输入路径："))
    
    if git_reader.check_git(file_path):
        print("此路径是git仓库\n即将执行检查日志操作------")
        print(git_reader.git_log(file_path))
        print("完成日志检查---------\n准备执行diff查询区别")
        print(git_reader.git_diff(file_path))
        print("完成diff查询---------\n准备创建markdown文件并写入日志")
        reports_dir = file_path/Path("learning_system/reports")
        reports_dir.mkdir(exist_ok=True)
        Path(reports_dir/f"{datetime.now().strftime("%Y-%m-%d")}.md").write_text(git_reader.generate_report(file_path))
        print(f"已添加{reports_dir/f"{datetime.now().strftime("%Y-%m-%d")}.md"}格式的git日志记录")
        print("---开始调用deepseek整理日志变化信息！请等待......---")
        deepseek_report = git_reader.deepseekapi(git_reader.git_stat(file_path))
        Path(reports_dir/f"{datetime.now().strftime("%Y-%m-%d")}deepseek分析.txt").write_text(deepseek_report)
        print(deepseek_report)
    else:
        print("此路径不为git仓库")
except FileNotFoundError:
    print("这个路径不存在！")
except NotADirectoryError:
    print("这个路径不是一个文件夹！")


