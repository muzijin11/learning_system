# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from mysql.connector import Error as DBError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app

client = TestClient(app)

MOCK_REPORT = {
    "id": 1,
    "report_date": "2025-05-19",
    "commit_count": 5,
    "report_content": "完成登录模块",
    "ai_analysis": "效率较高"
}

MOCK_REPORT_LIST = [MOCK_REPORT]


class TestGetReports:

    @patch("api.db.select_all_reports")
    def test_returns_200_with_list(self, mock_select):
        mock_select.return_value = MOCK_REPORT_LIST

        response = client.get("/reports")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

    @patch("api.db.select_all_reports")
    def test_returns_empty_list(self, mock_select):
        mock_select.return_value = []

        response = client.get("/reports")

        assert response.status_code == 200
        assert response.json() == []

    @patch("api.db.select_all_reports")
    def test_db_error_returns_500(self, mock_select):
        mock_select.side_effect = Exception("连接失败")

        response = client.get("/reports")

        assert response.status_code == 500


class TestGetReportLatest:

    @patch("api.db.select_latest")
    def test_returns_200_when_found(self, mock_select):
        mock_select.return_value = MOCK_REPORT

        response = client.get("/reports/latest")

        assert response.status_code == 200
        assert response.json()["id"] == 1

    @patch("api.db.select_latest")
    def test_returns_404_when_empty(self, mock_select):
        mock_select.return_value = None

        response = client.get("/reports/latest")

        assert response.status_code == 404

    @patch("api.db.select_latest")
    def test_db_error_returns_500(self, mock_select):
        mock_select.side_effect = Exception("连接失败")

        response = client.get("/reports/latest")

        assert response.status_code == 500


class TestGetReportByDate:

    @patch("api.db.select_report")
    def test_returns_200_when_found(self, mock_select):
        mock_select.return_value = MOCK_REPORT

        response = client.get("/reports/2025-05-19")

        assert response.status_code == 200
        assert response.json()["report_date"] == "2025-05-19"

    @patch("api.db.select_report")
    def test_returns_404_when_not_found(self, mock_select):
        mock_select.return_value = None

        response = client.get("/reports/2000-01-01")

        assert response.status_code == 404

    @patch("api.db.select_report")
    def test_db_error_returns_500(self, mock_select):
        mock_select.side_effect = Exception("连接失败")

        response = client.get("/reports/2025-05-19")

        # ⚠️ 这个测试会暴露 except DBError 的 bug
        # 修复前：返回 FastAPI 默认 500，detail 不是你写的那句话
        # 修复后：返回你自定义的 500
        assert response.status_code == 500