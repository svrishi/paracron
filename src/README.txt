ParaCron

Python 3.6 module providing cron-like task scheduler with REST interface.
Implemented using Python asyncio module. Uses one event loop to run the
non-blocking http server. Uses thread executor pool to launch a separate
event loop for task execution. Tasks are run as child processes with both
stdout and stderr redirected to a PIPE to capture output. Uses python
'schedule' module to track schedules and for schedule notifications.

Limitations:
* At this time project and task state is in-memory only. Plan is to
extend it to use redis for persistent store.
* Limited to single instance. Can be extended to push task execs
as messages to a distributed worker queue.
* Task exec needs to timeout.

Requirements:
* python version >= 3.6

Install:
* pip install -r ./requirements.txt
* cd src/ && python setup.py install

Usage:
* python -m paracron.server
* python -m unittest tests/test_restapi.py 

Sample API calls:

To create a project:
#> POST to /projects or /projects/<project name>
    curl --request POST \
      --url http://localhost:8080/projects/test \
      --header 'content-type: application/json' \
      --data '{ "name": "test", "interval": "seconds", "count": 5, "task_list": [ { "name": "ps", "cmd": "ps", "arg": "" }, {"name": "ls2", "cmd": "/bin/ls", "arg": "/tmp" } ] }'
#> GET to /projects to view list of projects and config
    curl --request GET --url http://localhost:8080/projects
#> GET to /projects/<project_name>/tasks to view task logs
    curl --request GET --url http://localhost:8080/projects/test/tasks
