# UCloud2Dida

一个自动同步北邮 UCloud 和课堂派(Ketangpai)待办事项和作业到滴答清单(TickTick)的 Python 工具。

## 功能特点

- 自动从 UCloud 和课堂派同步作业到滴答清单
- HTML 转 Markdown 的任务描述转换
- 可配置的同步时间间隔
- 适当的截止日期处理
- 具有指数退避的重试机制
- 自动避免重复任务创建

## 需求

- Python 3.13+
- 北邮 UCloud 账户
- 课堂派(Ketangpai)账户
- 滴答清单(TickTick)账户
- [uv](https://github.com/astral-sh/uv)

## 安装

1. 克隆此仓库：
    ```bash
    git clone https://github.com/yourusername/ucloud2dida.git
    cd ucloud2dida
    ```

2. 安装依赖：
    ```bash
    uv sync
    ```

## 配置

在根目录创建一个 `.env` 文件，内容如下：
client id与secret请参考 https://developer.dida365.com/docs#/openapi 获得(在应用设置里请将OAuth redirect URL设置为http://localhost:8080/callback)
project_id为你在滴答清单中负责存放作业的list的id，获取方式请见下
课堂派为可选项，token获取方式请在网页端登录课堂派，按F12使用开发者工具在网络请求中找到任意返回类型为json的请求并在其headers中获取token
课堂派课程id获取方式见下

```
# 滴答清单 API 凭证
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret
DIDA365_REDIRECT_URI=http://localhost:8080/callback
DIDA365_SERVICE_TYPE=dida365 #(或 TickTick)
DIDA365_PROJECT_ID=your_project_id_for_tasks

# 北邮凭证
BUPT_ACCOUNT=your_bupt_ucloud_student_id
BUPT_PASSWORD=your_bupt_ucloud_password

# 课堂派凭证
KETANGPAI_TOKEN=your_ketangpai_token
KETANGPAI_COURSE_ID=your_ketangpai_course_id

# 可选设置
SYNC_INTERVAL_SECONDS=3600  # 默认：1小时
MAX_RETRIES=3               # 默认：3次重试
```

### 获取滴答清单项目ID

如需查看可用的滴答清单项目及其ID，请运行：

```bash
uv run get_projects.py
```
### 获取课堂派课程ID

```bash
uv run get_course_id.py
```

## 使用方法

运行主同步脚本：

```bash
uv run main.py
```

该工具将：
1. 验证北邮 UCloud 身份
2. 验证滴答清单身份
3. 从 UCloud 和课堂派获取你的作业和待办事项
4. 在你的滴答清单账户中创建相应的任务
5. 按照指定的时间间隔（默认：每小时）继续同步

注意：第一次运行时请在具有浏览器的桌面环境下运行以完成滴答清单的认证关联并获取token，之后可以转移到服务器等环境中直接运行。