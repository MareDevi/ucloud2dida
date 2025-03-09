from src.ucloud2dida.api.ketangpai import ketangpai_api
from src.ucloud2dida.utils.logger import logger


def list_courses():
    """列出所有可用的课堂派课程"""
    try:
        if not ketangpai_api.token:
            logger.error("未配置课堂派 token，请先在 .env 文件中设置 KETANGPAI_TOKEN")
            return

        course_info = ketangpai_api.get_course_info()
        logger.info(f"获取到课程信息: {course_info['coursename']}")
        print("\n课程信息:")
        print(f"课程ID: {ketangpai_api.course_id}")
        print(f"课程名称: {course_info['coursename']}")
    except Exception as e:
        logger.error(f"获取课程信息时发生错误: {str(e)}")


if __name__ == "__main__":
    list_courses()
