from aiohttp import web
import aiohttp_jinja2
from paracron.models.db import Project
from paracron.events import update_project


@aiohttp_jinja2.template('homepage.jinja2')
def homepage(request):
    proj_list = list(Project.all())
    return {'projs': proj_list}


@aiohttp_jinja2.template('proj_tasks.jinja2')
async def get_proj_tasks(request):
    proj_name = request.match_info['name']
    proj = Project.query(proj_name)
    if not proj:
        raise web.HTTPBadRequest(text=str("Invalid project"))
    return {'project': proj.name, 'task_runs': proj.task_runs}


async def post_projects(request):
    params = await request.json()
    try:
        proj = Project(params)
    except ValueError as e:
        raise web.HTTPBadRequest(text=str(e))
    update_project(proj)
    return web.Response(text="Updated project config")


async def list_projects(request):
    projList = []
    for proj in Project.all():
        projList.append(proj.config)
    return web.json_response(projList)


async def get_project(request):
    proj_name = request.match_info['name']
    return web.json_response(Project.query(proj_name).config)


async def post_project(request):
    params = await request.json()
    proj_name = request.match_info['name']
    if proj_name != params.get('name', None):
        raise web.HTTPBadRequest(text="Project name mismatch"
                                 " in config and resource name")
    try:
        proj = Project(params)
    except ValueError as e:
        raise web.HTTPBadRequest(text=str(e))
    update_project(proj)
    return web.json_response(proj.config)


def add_routes(app):
    app.router.add_get('/', homepage)
    app.router.add_post('/projects', post_projects)
    app.router.add_get('/projects', list_projects)
    # Individual project routes
    proj_resource = app.router.add_resource('/projects/{name}')
    proj_resource.add_route('GET', get_project)
    proj_resource.add_route('POST', post_project)
    tasks_resource = app.router.add_resource('/projects/{name}/tasks')
    tasks_resource.add_route('GET', get_proj_tasks)
