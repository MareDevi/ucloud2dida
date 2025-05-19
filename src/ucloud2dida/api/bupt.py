from ..utils.logger import logger
from requests.auth import HTTPBasicAuth
import os
import requests
from dotenv import load_dotenv


class BuptAPI:
    def __init__(self):
        load_dotenv()
        self.account = os.getenv("BUPT_ACCOUNT")
        self.password = os.getenv("BUPT_PASSWORD")
        self.url = "https://ucloud.maredevi.workers.dev/"

    def get_todo_list(self):
        logger.info("正在获取待办事项列表")
        response = requests.get(
            f"{self.url}/undoneList", auth=HTTPBasicAuth(self.account, self.password)
        )
        data = response.json()
        todos = data["undoneList"]
        logger.info(f"成功获取到 {len(todos)} 个待办事项")
        for todo in todos:
            yield todo

    def get_assignment_detail(self, assignment_id):
        """获取作业详情"""
        logger.info(f"正在获取作业 {assignment_id} 的详情")
        response = requests.get(
            f"{self.url}/homework",
            params={"id": assignment_id},
            auth=HTTPBasicAuth(self.account, self.password),
        )

        data = response.json()
        return {
            "title": data["assignmentTitle"],
            "content": data["assignmentContent"],
            "resources": data.get("assignmentResource", []),
        }


# 创建全局API实例
bupt_api = BuptAPI()
get_todo_list = bupt_api.get_todo_list
get_assignment_detail = bupt_api.get_assignment_detail
