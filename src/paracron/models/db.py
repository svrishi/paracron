import numbers
import datetime
from validators.slug import slug


class Project:
    """
    Project defines the 'project' tasks configuration with recurring
    scheduling time defined as interval*count. For example, to run
    a project's tasks every 5 minutes then set interval to minutes
    and count to 5. Tasks list in project config defines the set
    of ordered tasks to execute.

    Sample project schedule configuration JSON format:
    {
    "name": "project name",
    "interval": "seconds/minutes/hours/days/weeks repeat time interval unit",
    "count": "quantity of time in interval units",
    "task_list": [ { "name": "task_A", "cmd": "process command", "arg": "" } ]
    }
    """
    _projectMap = {}

    def __init__(self, config):
        self.config = config
        (config_valid, errors) = self.validate()
        if not config_valid:
            raise ValueError(errors)
        self.name = config["name"]
        self.count = config["count"]
        self.interval = config["interval"]
        self.task_list = config["task_list"]
        now = datetime.datetime.utcnow().isoformat()
        self.created_at = now
        self.last_updated = now
        # for now, store task run history in memory
        self.task_runs = []
        # for now, store in memory
        Project._projectMap[self.name] = self

    def validate(self):
        errors = []
        if any(key not in self.config
                for key in ("name", "interval", "count", "task_list")):
            errors.append(('config',
                           'missing one or more required keys in config'))
            return (False, errors)
        if not slug(self.config["name"]):
            errors.append(('config', 'name must have alphanumeric, '
                           'underscore and hyphen chars only'))
        if (self.config["interval"] not in (
                "seconds", "minutes", "hours", "days", "weeks")):
            errors.append(('config',
                           'interval must be seconds/minutes/hours/days/weeks'))
        if (not isinstance(self.config["count"], numbers.Number)) or \
                (self.config["count"] < 1):
            errors.append(('config',
                           'count must be a positive non-zero number'))
        if len(self.config["task_list"]) == 0:
            errors.append(('config',
                           'task list array must be non-zero length'))
        catch_dup_task_names = {}
        for task_config in self.config["task_list"]:
            if any(key not in task_config for key in
                   ("name", "cmd", "arg")):
                errors.append(('config',
                               'task config missing required name/cmd/arg'))
                return (False, errors)
            if not slug(task_config["name"]):
                errors.append(('config', 'task name must have alphanumeric, '
                               'underscore and hyphen chars only'))
            if task_config["name"] in catch_dup_task_names:
                errors.append(('config', 'duplicate task in list of tasks'))
            catch_dup_task_names[task_config["name"]] = True
        if not errors:
            return (True, None)
        return (False, errors)

    def add_task_run(self, task_run):
        """History of task runs for a project are logged here"""
        self.task_runs.append(task_run)

    @classmethod
    def all(cls):
        for key, value in Project._projectMap.items():
            yield value

    @classmethod
    def query(cls, proj_name):
        if proj_name not in Project._projectMap:
            return None
        return Project._projectMap[proj_name]


class TaskRun:
    """
    TaskRun object captures the state and output from a specific
    individual execution aka run of a specific task in a project.
    """
    def __init__(self, proj_name, task_name, cmd, arg):
        self.proj_name = proj_name
        self.task_name = task_name
        self.cmd = cmd
        self.arg = arg
        now = datetime.datetime.utcnow().isoformat()
        self.started_at = now
        self.stdout_logs = self.stderr_logs = ""

    def run_name(self):
        return "%s.%s" % (self.proj_name, self.task_name)

    def ran_cmd(self):
        return "%s %s" % (self.cmd, self.arg)

    def done(self, stdout_logs, stderr_logs):
        self.stdout_logs = stdout_logs
        self.stderr_logs = stderr_logs
        self.done_at = datetime.datetime.utcnow().isoformat()
