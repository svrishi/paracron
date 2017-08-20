#!/usr/bin/env python3
import unittest
import asyncio
from aiohttp.test_utils import TestClient, setup_test_loop, teardown_test_loop
from paracron import server


class RestAPITestCase(unittest.TestCase):
    def setUp(self):
        self.loop = setup_test_loop(asyncio.new_event_loop)
        asyncio.set_event_loop(self.loop)
        asyncio.get_child_watcher().attach_loop(self.loop)
        self.app = server.create_app()
        self.client = TestClient(self.app, loop=self.loop)
        self.loop.run_until_complete(self.client.start_server())

    def tearDown(self):
        for task in asyncio.Task.all_tasks():
            task.cancel()
        self.loop.run_until_complete(self.client.close())
        self.loop.run_until_complete(self.app.shutdown())
        self.loop.run_until_complete(self.app.cleanup())
        teardown_test_loop(self.loop, fast=False)

    def test_root(self):
        async def test_get_route():
            resp = await self.client.get("/")
            assert resp.status == 200
            text = await resp.text()
            assert "Paracron Job Scheduler" in text

        try:
            self.loop.run_until_complete(test_get_route())
        except Exception:
            raise

    def test_post_project_errors(self):
        async def test_post_route():
            proj_config = {
                "name": "test invalid name",
                "interval": "years",
                "count": -1,
                "task_list": []
            }
            resp = await self.client.post("/projects", json=proj_config)
            assert resp.status == 400
            text = await resp.text()
            print(text)
            assert 'task list array must be non-zero length' in text
            assert 'name must have alphanumeric, ' \
                'underscore and hyphen chars only' in text
            assert 'interval must be seconds/minutes/hours/days/weeks' \
                in text
            assert 'count must be a positive non-zero number' in text
            assert 'task list array must be non-zero length' in text

        try:
            self.loop.run_until_complete(test_post_route())
        except Exception:
            raise

    def test_post_project_ok(self):
        async def test_post_route():
            proj_config = {
                "name": "test",
                "interval": "seconds",
                "count": 5,
                "task_list": [{
                    "name": "ls", "cmd": "/bin/ls", "arg": ""
                }]
            }
            resp = await self.client.post("/projects", json=proj_config)
            assert resp.status == 200
            text = await resp.text()
            assert "Updated project config" in text

        try:
            self.loop.run_until_complete(test_post_route())
        except Exception:
            raise

    def test_get_project_tasks(self):
        async def test_post_route():
            proj_config = {
                "name": "test",
                "interval": "seconds",
                "count": 5,
                "task_list": [{
                    "name": "ls", "cmd": "/bin/ls", "arg": ""
                }]
            }
            resp = await self.client.post("/projects", json=proj_config)
            assert resp.status == 200
            text = await resp.text()
            assert "Updated project config" in text
            await asyncio.sleep(10)
            resp = await self.client.get("/projects/test/tasks")
            assert resp.status == 200
            text = await resp.text()
            assert "test tasks run history" in text

        try:
            self.loop.run_until_complete(test_post_route())
        except Exception:
            raise
