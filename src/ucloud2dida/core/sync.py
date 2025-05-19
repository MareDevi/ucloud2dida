import os
import time
import asyncio
from datetime import datetime
import html2text
from dotenv import load_dotenv
from dida365 import Dida365Client, TaskCreate, TaskPriority

from ..utils.logger import logger
from ..api.bupt import get_todo_list, get_assignment_detail
from ..api.ketangpai import get_course_content


async def sync_tasks():
    """核心同步任务实现"""
    load_dotenv(override=True)
    logger.info("开始初始化 Dida365 客户端")
    client = Dida365Client()  # Will load from the specified .env file

    # First-time authentication:
    if not client.auth.token:
        logger.info("未检测到认证令牌，开始首次认证")
        await client.authenticate()
        logger.info("认证成功")

    project = await client.get_project(os.getenv("DIDA365_PROJECT_ID"))
    logger.info(f"成功获取项目：{project.name}")

    project_data = await client.get_project_with_data(project_id=project.id)
    logger.info(
        f"项目 {project_data.project.name} 当前包含 {len(project_data.tasks)} 个任务"
    )

    existing_tasks = {task.title for task in project_data.tasks}
    del project_data

    logger.info("开始获取待办事项列表")
    for todo in get_todo_list():  
        if todo["activityName"] in existing_tasks:
            logger.debug(f"任务 '{todo['activityName']}' 已存在，跳过")
            continue

        if todo["type"] == 3:
            logger.info(f"获取作业详情：{todo['activityName']}")
            assignment_detail = get_assignment_detail(todo["activityId"])
            content = html2text.HTML2Text().handle(assignment_detail["content"])
            await create_task(client, project.id, todo, content)
            del assignment_detail, content 
        elif todo["type"] == 4:
            await create_task(client, project.id, todo)

    # 处理课堂派任务
    if os.getenv("KETANGPAI_TOKEN"):
        logger.info("检测到课堂派令牌，开始同步课堂派任务")
        for assignment in get_course_content(): 
            if assignment["title"] in existing_tasks:
                logger.debug(f"课堂派任务 '{assignment['title']}' 已存在，跳过")
                continue
            await create_task(client, project.id, assignment)
    else:
        logger.info("未检测到课堂派令牌，跳过课堂派任务同步")


async def create_task(client, project_id, item, content=None):
    """创建任务的辅助函数"""
    task_create = TaskCreate(
        project_id=project_id,
        title=item.get("activityName", item.get("title")),
        content=content,
        priority=TaskPriority.MEDIUM,
        due_date=datetime.strptime(
            item.get("endTime", item.get("endtime")), "%Y-%m-%d %H:%M:%S"
        ),
        is_all_day=False,
        time_zone="UTC",
    )
    await client.create_task(task_create)
    logger.info(f"成功创建任务：{task_create.title}")


async def wait_with_interrupt(event, seconds):
    """等待指定的秒数，可被中断事件打断"""
    try:
        await asyncio.wait_for(event.wait(), timeout=seconds)
        return event.is_set()
    except asyncio.TimeoutError:
        return False


async def execute_with_retry(task_func, max_retries, shutdown_event):
    """使用指数退避策略执行任务，有重试机制"""
    start_time = time.time()
    retry_count = 0

    while retry_count < max_retries:
        try:
            await task_func()
            logger.info("同步任务完成")
            return True, time.time() - start_time
        except Exception as e:
            retry_count += 1
            wait_time = min(30, 2**retry_count)
            logger.error(f"同步任务出错 (尝试 {retry_count}/{max_retries}): {str(e)}")

            if retry_count < max_retries:
                logger.info(f"将在 {wait_time} 秒后重试")
                if await wait_with_interrupt(shutdown_event, wait_time):
                    return False, time.time() - start_time
            else:
                logger.error("达到最大重试次数，等待下一个计划执行周期")

    return False, time.time() - start_time


async def perform_sync_cycle(shutdown_event, sync_interval, max_retries):
    """执行一个完整的同步周期，包括任务执行和等待"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"开始在 {current_time} 执行同步任务")

    success, elapsed = await execute_with_retry(sync_tasks, max_retries, shutdown_event)

    if shutdown_event.is_set():
        return False

    wait_time = max(1, sync_interval - elapsed)
    logger.info(f"等待 {wait_time:.1f} 秒后再次执行")
    interrupted = await wait_with_interrupt(shutdown_event, wait_time)

    return not interrupted
