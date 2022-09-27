"""Queue management."""
import json as pyjson

import yaml
import yaml as pyyaml

from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.util import path_expand


class Job:
    """
    A job is an object that has a name and a command. This name is paired
    to the command.
    """

    def __init__(self, name=None, command=None, kind=None, status=None):
        """

        # this is not realy that good, as we need to be able to overwrite from **data ...
        # atend we want to see that values are defined, and if they have not been passed
        # we create the defaults

        :param name:
        :type name:
        :param command:
        :type command:
        :param kind: the kind of teh job: local, ssh, slurm remote-slurm
        :type kind: str
        :param status:
        :type status:
        """
        self.name = name
        self.user = None
        self.label = None
        self.command = command
        self.status = 'defined'
        self.output = None
        self.output_file = None
        self.error_file = None
        self.error = None
        self.kind = kind
        self.progress = 0
        self.created = DateTime.now()
        self.modified = DateTime.now()

    def __str__(self):
        d = self.__dict__
        return str(yaml.dump(d, indent=2))

    @property
    def dict(self):
        # check if dict is ok
        d = self.__dict__
        return d

    def set(self, state):
        self.status = state
        self.modified = DateTime.now()

    def update(self):
        self.modified = DateTime.now()
        raise NotImplementedError("the update function will be implemented "
                                  "based on type of job")

    def run(self, dryrun=False):
        if not dryrun:
            if self.kind in ["local"]:
                r = Shell.run(self.command)
            elif self.kind in ["ssh"]:
                raise NotImplementedError
            elif self.kind in ["local-slurm"]:
                raise NotImplementedError
            elif self.kind in ["remote-slurm"]:
                raise NotImplementedError

    def get_progress(self):
        pass
        # depends on job type, festches progress from output file which may
        # be local, or remote


class Queue:
    """
        The queue is data structure that holds the jobs. This means that
        the data structure will be a dictionary because it is holding all
        names: commands of the jobs. The queue will have several commands:
        instantiate, add, remove, run, get, and list.
    """

    def __init__(self, name=None):
        """
        Initializes the queue object

        :param name:
        :return: creates the queue object
        """

        if name is None:
            self.name = 'localhost'
        else:
            self.name = name

        self.jobs = {}

    def add(self, name, command):
        """
        Creates a job using the name and command parameters and then
        adds this job to the correct queue

        :param name:
        :param command:
        :return: edits a queue that was created by adding an element
        """
        job = Job(name, command)
        self.jobs[job.name] = job

    def remove(self, name):
        """
        Takes a job name and removes the specified job

        :param name:
        :returns: updated queue structure
        """
        self.jobs.pop(name)

    def list(self):
        """
        Takes a queue and returns the elements that are in the queue, in the
        correct order that they are supposed to be in.

        :return: list of the jobs that are in the queue object
        """
        for name in self.jobs:
            print(name, self.jobs.get(name))

    def run(self, scheduler):
        """
        Take a specific queue and then accesses all jobs and runs the
        commands of the jobs in the correct order. The order is FIFO (first
        in first out).

        :param scheduler:
        :return: the commands that are in the queue, one at a time
        """
        if scheduler.lower() == 'fifo':
            for name, job in self.jobs.items():
                print(job)
                c = self.jobs.get(job)
                r = Shell.run(c)
                print(f"run queue={self.name} job={name} command={c}:", r)
        else:
            print("LIFO and PQ are not yet implemented")


class Queues:
    """
    Queues holds all of the queues
    with their corresponding names. It is a meta-queue, essentially. The queues
    class will be a dictionary of dictionaries of jobs, which are
    job names and commands.

    An example command would likely look like:
        cms cc queues list --queues=ab
    """

    # def __init__(self, filename=None, database='yamldb'):
    def __init__(self, filename=None, database=None):
        """
        Initializes the giant queue structure.
        """

        if filename is None:
            filename = "~/.cloudmesh/queue/queue.yamldb"

        if database is not None:
            self.database = database
        else:
            self.database = 'yamldb'

        if self.database == 'yamldb':
            from cloudmesh.cc.db.yamldb.database import Database as QueueDB
        else:
            # we have not implemented any other database outside of yamldb
            raise NotImplementedError

        self.db = QueueDB(filename=filename)
        self.counter = 0

    def save(self):
        """
        save the queue to persistent storage
        """
        self.db.save()

    def load(self):
        self.db.load()

    @property
    def filename(self):
        return self.db["filename"]

    @property
    def queues(self):
        return self.db.queues

    @property
    def config(self):
        return self.db.data['config']

    def add(self, name: str, job: str, command: str):
        """
        Adds a queue to the queues.

        cms cc queues add --queues= abc --queue=d

        """
        self.db.load()
        self.queues[name][job] = {"name": job,
                                  "command": command,
                                  "queue": name,
                                  "status": 'ready',
                                  "error": None}
        self.save()

    def create(self, name: str):
        """
        Create a queue

        cms cc queues add --queues= abc --queue=d
        """
        self.queues[name] = {}
        self.save()

    def remove(self, name):
        """
        removes a queue from the queues

        cms cc queues remove --queues=abc --queue=c
        """
        del self.queues[name]
        self.save()

    def run(self, scheduler):
        """
        Runs the queues in the order specified.
        :param scheduler:
        :return: the commands that are issued from the jobs.
        """
        if scheduler.lower() == 'fifo':
            self.counter = 0
            for queue in self.queues:
                q = self.queues[queue]
                for job in q:
                    c = self.queues[queue][job]['command']
                    print(c)
                    self.queues[queue][job]['status'] = 'running'
                    r = Shell.run(c)
                    self.queues[queue][job]['output'] = r
                    if 'ERROR' in r:
                        self.queues[queue][job]['status'] = 'failed'
                    else:
                        self.queues[queue][job]['status'] = 'done'
                    self.counter = self.counter + 1
                    print(r)

                # self.queues[queue].run(scheduler=scheduler)

        self.save()

    def list(self):
        """
        Returns a list of the queues that are in the queue
        :return:
        """
        for each in self.queues:
            print(each)

        # no save needed as just list

    def dict(self):
        d = {}
        for each in self.queues:
            d[each] = {}
            for job, command in self.queues.jobs.items():
                d[each][job] = command
        return d

    def __len__(self):
        return len(self.queues)

    def get(self, q):
        return self.queues[q]

    def __str__(self):
        d = {"config": self.db.data["config"],
             "queue": self.queues}
        return pyyaml.dump(d, indent=2)

        # result = str(self.queues)
        # return result
        # return str(yaml.dump(self.queues, indent=2))

    @property
    def yaml(self):
        return pyyaml.dump(self.queues, indent=2)

    @property
    def json(self):
        return pyjson.dumps(dict(self.queues), indent=2)

    def info(self):
        return self.db.info()

    def __getitem__(self, item):
        return self.queues[item]
