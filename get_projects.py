import asyncio
from dida365 import Dida365Client

client = Dida365Client()


async def get_projects_from_client():
    if not client.auth.token:
        await client.authenticate()

    # List all projects
    projects = await client.get_projects()

    for project in projects:
        print(f"Project: {project.name} id: {project.id}")


# Run the async function
asyncio.run(get_projects_from_client())
