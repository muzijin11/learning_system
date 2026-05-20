# tests/test_db.py

import pytest
from unittest.mock import patch, MagicMock
import db


def make_mock_conn(mock_cursor):
    """
    构造标准的 mock 连接链，避免每个测试重复写
    返回 mock_conn，已绑定好 cursor
    """
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    return mock_conn


class TestInsertReports:

    @patch("db.connect_db")
    def test_insert_success_returns_lastrowid(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 42  # 模拟数据库返回的新行 ID
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.insert_reports(
            report_date="2025-05-19",
            commit_count=5,
            report_content="完成了登录模块",
            ai_analysis="工作效率较高"
        )

        assert result == 42
        mock_cursor.execute.assert_called_once()  # SQL 被执行了
        # 验证 SQL 参数正确传入
        args = mock_cursor.execute.call_args[0]  # 取位置参数
        assert "2025-05-19" in args[1]
        assert 5 in args[1]

    @patch("db.connect_db")
    def test_insert_with_none_optional_fields(self, mock_connect):
        """report_content 和 ai_analysis 可以为 None"""
        mock_cursor = MagicMock()
        mock_cursor.lastrowid = 1
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.insert_reports(report_date="2025-05-19")

        assert result == 1

    @patch("db.connect_db")
    def test_insert_db_connection_fails(self, mock_connect):
        mock_connect.side_effect = Exception("MySQL connection refused")
        
        result = db.insert_reports("2025-05-19")
        
        assert result is None  # 现在函数捕获了异常，返回 None


class TestSelectAllReports:

    @patch("db.connect_db")
    def test_returns_list(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"id": 1, "report_date": "2025-05-19", "commit_count": 5,
             "report_content": "test", "ai_analysis": "ok"},
            {"id": 2, "report_date": "2025-05-18", "commit_count": 3,
             "report_content": "test2", "ai_analysis": "ok2"},
        ]
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.select_all_reports()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["report_date"] == "2025-05-19"

    @patch("db.connect_db")
    def test_returns_empty_list_when_no_data(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.select_all_reports()

        assert result == []

    @patch("db.connect_db")
    def test_select_reports_db_fails(self, mock_connect):
        mock_connect.side_effect = Exception("连接失败")
        result = db.select_all_reports()
        assert result is None


class TestSelectReport:

    @patch("db.connect_db")
    def test_returns_dict_when_found(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "report_date": "2025-05-19",
            "commit_count": 5,
            "report_content": "test",
            "ai_analysis": "ok"
        }
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.select_report("2025-05-19")

        assert result is not None
        assert result["report_date"] == "2025-05-19"

    @patch("db.connect_db")
    def test_returns_none_when_not_found(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.select_report("2000-01-01")

        assert result is None


    @patch("db.connect_db")
    def test_select_report_db_fails(self, mock_connect):
        mock_connect.side_effect = Exception("连接失败")
        result = db.select_report("2025-05-20")
        assert result is None

class TestSelectLatest:

    @patch("db.connect_db")
    def test_returns_latest_report(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": 99,
            "report_date": "2025-05-19",
            "commit_count": 10,
            "report_content": "最新日报",
            "ai_analysis": "分析结果"
        }
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.select_latest()

        assert result["id"] == 99

    @patch("db.connect_db")
    def test_returns_none_when_table_empty(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value = make_mock_conn(mock_cursor)

        result = db.select_latest()

        assert result is None

    @patch("db.connect_db")
    def test_select_latest_db_fails(self, mock_connect):
        mock_connect.side_effect = Exception("连接失败")
        result = db.select_latest()
        assert result is None


class TestUpdateReport:

    @patch("db.connect_db")
    def test_update_executes_sql(self, mock_connect):
        mock_cursor = MagicMock()
        mock_connect.return_value = make_mock_conn(mock_cursor)

        db.update_report_ai_analysis(id=1, value="新的AI分析内容")

        mock_cursor.execute.assert_called_once()
        args = mock_cursor.execute.call_args[0]
        assert "新的AI分析内容" in args[1]
        assert 1 in args[1]


    @patch("db.connect_db")
    def test_update_db_fails(self, mock_connect):
        mock_connect.side_effect = Exception("连接失败")
        result = db.update_report_ai_analysis(id=-1,value="ai分析内容")
        assert result is None