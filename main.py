import os
import time
import asyncio
import signal
import logging
import html2text
import platform
from datetime import datetime
from dotenv import load_dotenv
from bupt_api import get_todo_list, get_assignment_detail
from dida365 import Dida365Client, TaskCreate, TaskPriority
from ketangpai import get_course_content


async def sync_tasks():
    load_dotenv(".env")
    client = Dida365Client()  # Will load from the specified .env file

    # First-time authentication:
    if not client.auth.token:
        await client.authenticate()

    project = await client.get_project(os.getenv("DIDA365_PROJECT_ID"))

    project_data = await client.get_project_with_data(project_id=project.id)
    print(f"Project {project_data.project.name} has {len(project_data.tasks)} tasks")

    tasks = []
    for i in project_data.tasks:
        tasks.append(i.title)

    # Get the user's todo list
    todos = get_todo_list()

    for i in todos:
        if i["activityName"] in tasks:
            pass
        else:
            if i["type"] == 3:
                assignment_detail = get_assignment_detail(i["activityId"])
                print(f"Creating task for {i['activityName']}")

                content = assignment_detail["content"]
                # Convert HTML to markdown
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = False
                content = h.handle(content)
                _task = await client.create_task(
                    TaskCreate(
                        project_id=project.id,
                        title=i["activityName"],
                        content=content,
                        priority=TaskPriority.MEDIUM,
                        due_date=datetime.strptime(i["endTime"], "%Y-%m-%d %H:%M:%S"),
                        is_all_day=False,
                        time_zone="UTC",
                    )
                )
            elif i["type"] == 4:
                print(f"Creating task for {i['activityName']}")
                _task = await client.create_task(
                    TaskCreate(
                        project_id=project.id,
                        title=i["activityName"],
                        priority=TaskPriority.MEDIUM,
                        due_date=datetime.strptime(i["endTime"], "%Y-%m-%d %H:%M:%S"),
                        is_all_day=False,
                        time_zone="UTC",
                    )
                )

    # Get the course content if KETANGPAI_TOKEN exists
    if os.getenv("KETANGPAI_TOKEN"):
        undone_assigenments = get_course_content()

        for i in undone_assigenments:
            if i["title"] in tasks:
                pass
            else:
                print(f"Creating task for {i['title']}")
                _task = await client.create_task(
                    TaskCreate(
                        project_id=project.id,
                        title=i["title"],
                        priority=TaskPriority.MEDIUM,
                        due_date=datetime.strptime(i["endtime"], "%Y-%m-%d %H:%M:%S"),
                        is_all_day=False,
                        time_zone="UTC",
                    )
                )


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
            logging.info("同步任务完成")
            return True, time.time() - start_time
        except Exception as e:
            retry_count += 1
            wait_time = min(30, 2**retry_count)
            logging.error(f"同步任务出错 (尝试 {retry_count}/{max_retries}): {str(e)}")

            if retry_count < max_retries:
                logging.info(f"将在 {wait_time} 秒后重试")
                if await wait_with_interrupt(shutdown_event, wait_time):
                    return False, time.time() - start_time
            else:
                logging.error("达到最大重试次数，等待下一个计划执行周期")

    return False, time.time() - start_time


async def perform_sync_cycle(shutdown_event, sync_interval, max_retries):
    """执行一个完整的同步周期，包括任务执行和等待"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"开始在 {current_time} 执行同步任务")

    success, elapsed = await execute_with_retry(sync_tasks, max_retries, shutdown_event)

    if shutdown_event.is_set():
        return False

    wait_time = max(1, sync_interval - elapsed)
    logging.info(f"等待 {wait_time:.1f} 秒后再次执行")
    interrupted = await wait_with_interrupt(shutdown_event, wait_time)

    return not interrupted


async def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 从环境变量获取同步间隔时间，默认为3600秒（1小时）
    sync_interval = int(os.getenv("SYNC_INTERVAL_SECONDS", 3600))
    max_retries = int(os.getenv("MAX_RETRIES", 3))

    # 设置中断处理
    shutdown_event = asyncio.Event()

    def signal_handler():
        logging.info("收到终止信号，准备退出...")
        shutdown_event.set()

    # 根据操作系统类型设置不同的信号处理方式
    system = platform.system()
    loop = asyncio.get_running_loop()

    if system == "Windows":
        # Windows系统下使用SIGINT (Ctrl+C) 信号处理
        signal.signal(signal.SIGINT, lambda signum, frame: signal_handler())
        # Windows下无法使用loop.add_signal_handler，也不支持SIGTERM
        logging.info("运行在Windows系统上，已设置SIGINT (Ctrl+C) 信号处理")
    else:
        # Unix/Linux/macOS系统下使用事件循环的信号处理器
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
        logging.info(f"运行在{system}系统上，已设置SIGINT和SIGTERM信号处理")

    logging.info(f"同步服务启动，间隔时间设置为 {sync_interval} 秒")

    while not shutdown_event.is_set():
        if not await perform_sync_cycle(shutdown_event, sync_interval, max_retries):
            break

    logging.info("同步服务已停止")


if __name__ == "__main__":
    asyncio.run(main())
