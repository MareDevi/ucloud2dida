import requests
import dotenv
import os
from datetime import datetime

dotenv.load_dotenv(".env")

def get_semeseter_list():
    url = "https://openapiv5.ketangpai.com/CourseApi/semesterList"
    headers = {
        "Content-Type": "application/json",
        "token": os.getenv("KETANGPAI_TOKEN"),
    }
    response = requests.post(url, headers=headers)

    courses = response.json()["data"]["topcourses"]

    for course in courses:
        print(course["coursename"])
        print(course["id"])


def get_course_info():
    url = "https://openapiv5.ketangpai.com//CourseBigDataApi/getCourseBaseDataV2"
    headers = {
        "Content-Type": "application/json",
        "token": os.getenv("KETANGPAI_TOKEN"),
    }
    data = {"courseid": os.getenv("KETANGPAI_COURSE_ID")}
    response = requests.post(url, headers=headers, json=data)
    course_info = response.json()["data"]

    return course_info


def get_course_content():
    url = "https://openapiv5.ketangpai.com//FutureV2/CourseMeans/getCourseContent"
    headers = {
        "Content-Type": "application/json",
        "token": os.getenv("KETANGPAI_TOKEN"),
    }
    data = {
        "courseid": os.getenv("KETANGPAI_COURSE_ID"),
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
    response = requests.post(url, headers=headers, json=data)

    assigenments = response.json()["data"]["list"]
    undone_assigements = []
    for assigement in assigenments:
        if assigement["timestate"] == 2:
            course_info = get_course_info()
            title = course_info["coursename"] + "-" + assigement["title"]
            # return as json include title and endtime
            # make endtime from timestamp to string :%Y-%m-%d %H:%M:%S
            endtime = datetime.fromtimestamp(int(assigement["endtime"])).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            undone_assigements.append({"title": title, "endtime": endtime})

    return undone_assigements