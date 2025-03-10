from ..utils.logger import logger
from ..auth.bupt_auth import get_co_and_sa
import os
import json
import requests
from dotenv import load_dotenv


class BuptAPI:
    def __init__(self):
        load_dotenv()
        self.account = os.getenv("BUPT_ACCOUNT")
        self.password = os.getenv("BUPT_PASSWORD")
        self._setup_endpoints()

    def _setup_endpoints(self):
        """设置API端点"""
        self.base_url = "https://apiucloud.bupt.edu.cn"
        self.file_url = "https://fileucloud.bupt.edu.cn/ucloud/document/"
        self.assignment_file_url = f"{self.base_url}/blade-source/resource/filePath"

    def _refresh_auth(self):
        """刷新认证信息"""
        logger.info("刷新北邮认证信息")
        get_co_and_sa(self.account, self.password)

        with open("auth.json", "r") as file:
            account_data = json.load(file)
            self.tenant_id = account_data["tenant_id"]
            self.user_id = account_data["user_id"]
            self.auth_token = account_data["auth_token"]
            self.blade = account_data["blade"]

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Authorization": self.auth_token,
            "Tenant-Id": self.tenant_id,
            "Blade-Auth": self.blade,
        }

    def get_todo_list(self):
        """获取待办事项列表"""
        logger.info("正在获取待办事项列表")
        self._refresh_auth()
        response = requests.get(
            f"{self.base_url}/ykt-site/site/student/undone",
            headers=self.headers,
            params={"userId": self.user_id},
        )
        data = response.json()
        todos = data["data"]["undoneList"]
        logger.info(f"成功获取到 {len(todos)} 个待办事项")
        return todos

    def get_assignment_detail(self, assignment_id):
        """获取作业详情"""
        logger.info(f"正在获取作业 {assignment_id} 的详情")
        response = requests.get(
            f"{self.base_url}/ykt-site/work/detail",
            headers=self.headers,
            params={"assignmentId": assignment_id},
        )
        data = response.json()["data"]
        return {
            "title": data["assignmentTitle"],
            "content": data["assignmentContent"],
            "resources": data.get("assignmentResource", []),
        }


# 创建全局API实例
bupt_api = BuptAPI()
get_todo_list = bupt_api.get_todo_list
get_assignment_detail = bupt_api.get_assignment_detail
