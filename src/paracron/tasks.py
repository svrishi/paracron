import asyncio
import asyncio.subprocess
from paracron.models.db import TaskRun


@asyncio.coroutine
def exec_task(project, task_config):
    print("executing task", task_config)
    task_cmd = task_config["cmd"]
    task_arg = task_config["arg"]
    run = TaskRun(project.name, task_config["name"], task_cmd, task_arg)

    try:
        # Create the subprocess, redirect the standard output and standard error
        # into pipes
        if len(task_arg) > 0:
            create = asyncio.create_subprocess_exec(
                task_cmd, task_arg, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        else:
            create = asyncio.create_subprocess_exec(
                task_cmd, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
        proc = yield from create

        # Read output
        data = yield from proc.stdout.read()
        out_text = data.decode('ascii')

        # Read stderr
        data = yield from proc.stderr.read()
        err_text = data.decode('ascii')

        # Wait for the subprocess exit
        yield from proc.wait()

        run.done(out_text, err_text)
        project.add_task_run(run)
    except Exception as e:
        run.done("", "Exception when executing task %s" % e)
        project.add_task_run(run)


# "task_list": [ { "name": "task_A", "cmd": "process command", "arg": "" } ]
@asyncio.coroutine
def run_task(project):
    print("Executing task list of:", project.name)
    try:
        for task in project.task_list:
            # Task list specifies dependencies so yield from to ensure
            # completion of the task before starting the next
            yield from asyncio.ensure_future(exec_task(project, task))
    except Exception:
        raise
