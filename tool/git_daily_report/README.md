# git日报分析

## 项目简介
获取git日志和变化调用deepseek进行分析

## 技术栈
python mysql fastapi
## 项目结构
```
tool/git_daily_report/
├── main.py        # 主程序，生成日报并存入数据库
├── api.py         # FastAPI 接口服务
├── db.py          # 数据库操作封装
├── git_reader.py  # Git 日志读取与 AI 分析
└── README.md
```
## 环境准备
- Python 版本：3.12.3
- 依赖安装命令 :pip install "fastapi[standard]" mysql-connector-python openai python-dotenv
- .env 配置项说明:  
deepseekapikey = "deepseek apikey"  
repo_path = "git仓库路径"  
DB_HOST="数据库ip"  
DB_PORT=数据库端口  
DB_USER="数据库账户"  
DB_PASSWORD="数据库密码"  
DB_NAME="数据库名称"  

## 数据库初始化
数据库字段信息:  
CREATE TABLE daily_reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_date DATE NOT NULL,
    commit_count INT NOT NULL DEFAULT 0,
    report_content LONGTEXT,
    ai_analysis LONGTEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

## 使用方式
### 生成日报
执行main.py获取日报，修改内容和ai分析信息并存入reports和数据库
### 启动 API 服务
uvicorn api:app --reload
## API 接口
| 接口 | 方法 | 说明 | 无数据时 |
|------|------|------|----------|
| /reports | GET | 返回所有日报列表 | 返回空列表 |
| /reports/latest | GET | 返回最新一条日报 | 返回 404 |
| /reports/{date} | GET | 返回指定日期日报，date 格式 YYYY-MM-DD | 返回 404 |