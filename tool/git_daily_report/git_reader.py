from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
import os
#导入.env环境变量
load_dotenv()

#设置全局当日时间变量
today_time = datetime.now().strftime("%Y-%m-%d 00:00:00")

#检查路径是否存在或为文件夹
def check_path(text:str)->Path:
        text = Path(text)
        if not text.exists():
            raise FileNotFoundError(f"路径不存在，{text}")
        if not text.is_dir():
            raise NotADirectoryError(f"此路径不是文件夹路径，{text}")
        
        return text
        
#检查路径是否为git仓库
def check_git(path:Path):
    return (path / ".git").is_dir()
         


#获取当日简单日志
def git_log(path:Path):
    result = subprocess.run(["git","log","--oneline","--format=%h|%an|%ad|%s","--date=short",f"--since={today_time}"],cwd=path,capture_output=True,text=True)
    return result.stdout


#获取当日全部commint信息
def git_diff(path:Path):
    result = subprocess.run(["git","log","-p",f"--since={today_time}"],cwd=path,capture_output=True,text=True)
    return result.stdout

def git_stat(path:Path):
     result = subprocess.run(["git", "log", "--stat", f"--since={today_time}", "--format=%h %s"],cwd=path,capture_output=True,text=True)
     return result.stdout

#获取今日开发报告并保存为markdown文件
def generate_report(path:Path):
    markdown = {}
    log = git_log(path)
    diff = git_diff(path)
    markdown["commitnumber"] = len(log.splitlines())
    markdown["commitinfo"] = log
    markdown["commitdiff"] = diff
    commit_lines = ""
    for a in log.splitlines():
         parts = a.split("|")
         commit_lines += f"- `{parts[0]}` {parts[2]} {parts[1]} — {parts[3]}\n"
    return f"""# 今日开发报告 - {today_time}
## Commit 记录
今日共{markdown['commitnumber']}次
commit信息为:
{commit_lines}
## 代码改动\n\n```diff\n{markdown['commitdiff']}\n```
"""

#调用deepseek任命为"负责分析我提供给你的git记录"
def deepseekapi(stat:str):
    client = OpenAI(
    api_key=os.getenv('deepseekapikey'),
    base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": "你负责分析我提供给你的git记录。如果用户提供的内容为空或没有任何git记录，你必须直接回复--今日无提交记录--，不要编造任何内容。"},
            {"role": "user", "content": f"以下是今日git记录\n{stat}\n帮我简单分析变更信息"},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    return response.choices[0].message.content



    
    
