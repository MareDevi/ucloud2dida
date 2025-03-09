from ..utils.logger import logger
import requests
import os
from datetime import datetime
from dotenv import load_dotenv


class KetangpaiAPI:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("KETANGPAI_TOKEN")
        self.course_id = os.getenv("KETANGPAI_COURSE_ID")
        self.base_url = "https://openapiv5.ketangpai.com"
        self.headers = {"Content-Type": "application/json", "token": self.token}

    def get_course_info(self):
        """获取课程信息"""
        url = f"{self.base_url}/CourseBigDataApi/getCourseBaseDataV2"
        response = requests.post(
            url, headers=self.headers, json={"courseid": self.course_id}
        )
        return response.json()["data"]

    def get_course_content(self):
        """获取课程内容"""
        if not self.token:
            logger.warning("未配置课堂派token，跳过获取课程内容")
            return []

        logger.info("正在获取课堂派课程内容")
        url = f"{self.base_url}/FutureV2/CourseMeans/getCourseContent"
        data = {
            "courseid": self.course_id,
            "contenttype": 4,
            "dirid": 0,
            "lessonlink": [],
            "sort": [],
            "page": 1,
            "limit": 50,
            "desc": 3,
            "courserole": 0,
            "vtr_type": "",
        }

        response = requests.post(url, headers=self.headers, json=data)
        assignments = response.json()["data"]["list"]
        undone = []

        for assignment in assignments:
            if assignment["timestate"] == 2:
                course_info = self.get_course_info()
                title = f"{course_info['coursename']}-{assignment['title']}"
                endtime = datetime.fromtimestamp(int(assignment["endtime"])).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                undone.append({"title": title, "endtime": endtime})

        logger.info(f"获取到 {len(undone)} 个未完成的课堂派作业")
        return undone


# 创建全局API实例
ketangpai_api = KetangpaiAPI()
get_course_content = ketangpai_api.get_course_content

# 导出函数
__all__ = ["get_course_content", "ketangpai_api"]
