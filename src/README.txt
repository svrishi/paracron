ParaCron

Python 3.6 module providing cron-like task scheduler with REST interface.
Implemented using Python asyncio module. Uses one event loop to run the
non-blocking http server. Uses thread executor pool to launch a separate
event loop for task execution. Tasks are run as child processes with both
stdout and stderr redirected to a PIPE to capture output. Uses python
'schedule' module to be notified of job execution.

Limitations:
* At this time project and task state is in-memory only. Plan is to
extend it to use redis for persistent store.
* Limited to single instance. Can be extended to push task execs
as messages to a distributed worker queue.
* Task exec needs to timeout.
