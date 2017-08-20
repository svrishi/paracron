import asyncio
import schedule
from paracron.tasks import run_task
import concurrent.futures


def run_project_job(project):
    print("Running project job:", project.name)
    try:
        task = asyncio.ensure_future(run_task(project))
    except Exception as e:
        raise


def update_project(project):
    print(project.name, project.config)
    # first delete the previous project config
    schedule.clear(project.name)
    # next, create the schedule events by project config
    schedule_fn = getattr(schedule.every(project.count),
                          project.interval)
    schedule_fn.do(run_project_job, project).tag(project.name)


@asyncio.coroutine
def run_pending_jobs(loop, app):
    try:
        while loop.is_running() and app["job_thread"]["alive"]:
            schedule.run_pending()
            # sleep 1 sec between checks for any new/pending jobs
            yield from asyncio.sleep(1)
    except Exception:
        raise


@asyncio.coroutine
def run_schedule_loop(app):
    try:
        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(5)
        loop.set_default_executor(executor)

        def run_pending_jobs_thread():
            # Use a new event loop to launch jobs to ensure we don't
            # block the main event loop due to long running jobs.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                task = loop.create_task(run_pending_jobs(loop, app))
                loop.run_until_complete(task)
            except Exception:
                task.cancel()

        fut = loop.run_in_executor(executor, run_pending_jobs_thread)
        yield from asyncio.wait_for(fut, None)
    except Exception:
        print("Cancelled run schedule loop...wait for thread to terminate!")
        fut.cancel()
    finally:
        app["job_thread"]["alive"] = False
        executor.shutdown(wait=True)
