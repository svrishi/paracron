#!/usr/bin/env python3
import os
import jinja2
import asyncio
import aiohttp_jinja2
from aiohttp import web
from paracron.routes import add_routes
from paracron.events import run_schedule_loop

# We must call the get_child_watcher() function in the main thread to
# instantiate the child watcher. This is to support running subprocess from
# threads.
# https://docs.python.org/3/library/asyncio-subprocess.html#subprocess-and-threads
asyncio.get_child_watcher().attach_loop(asyncio.get_event_loop())


async def start_background_tasks(app):
    # use global alive flag to teardown the job thread
    app["job_thread"] = {"alive": True}
    # start a background task in event loop to handle scheduler events
    app['run_schedule_loop_task'] = app.loop.create_task(run_schedule_loop(app))


async def cleanup_background_tasks(app):
    app["job_thread"]["alive"] = False
    app['run_schedule_loop_task'].cancel()
    await app['run_schedule_loop_task']


def create_app():
    app = web.Application()
    # setup jinja2 templates
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(
                             os.path.join(os.path.dirname(__file__),
                                          'templates')))
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    add_routes(app)
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='127.0.0.1', port=8080)
