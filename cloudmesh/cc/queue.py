import yaml as pyyaml
import json as pyjson
from cloudmesh.common.Shell import Shell, Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_mac, os_is_windows, os_is_linux
import os
from cloudmesh.common.DateTime import DateTime

"""
    This is a program that allows for the instantiation of jobs and then
    allowing those jobs to be manipulated in a queue. These manipulations
    are add, create, remove, list, and run. This way, once a remote computer
    (such as Rivanna) is accessed, the jobs that need to be executed can be).

    Below are the objects and what they can do with examples of the type of
    command that would theoretically be run in the command line.
"""


class Job:
    """
        A job is an object that has a name and a command. This name is paired
        to the command.
    """

    def __init__(self, name=None, command=None, kind=None, status=None):
        """

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
        self.command = command
        self.status = status
        self.kind = kind
        self.created = DateTime.now()
        self.modified = DateTime.now()

    def __str__(self):
        return f'Job Name= {self.name}, Command={self.command}'

    def set(self, state):
        self.status = state
        self.modified = DateTime.now()

    def update(self):
        self.modified = DateTime.now()
        raise NotImplementedError("the update function will be implemented "
                                  "based on type of job")



class Queue:
    """
        The queue is data structure that holds the jobs. This means that
        the data structure will be a dictionary because it is holding all of
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
        self.jobs[job.name] = job.command

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
        Take a specific queue and then accesses all of the jobs and runs the
        commands of the jobs in the correct order. The order is FIFO (first
        in first out).

        :param scheduler:
        :return: the commands that are in the queue, one at a time
        """
        if scheduler.lower() == 'fifo':
            for name in self.jobs:
                c = self.jobs.get(name)
                r = Shell.run(c)
                print(f"run queue={self.name} job={name} command={c}:", r)
        else:
            print("LIFO and PQ are not yet implemented")


class Queues:
    """
    The Queues data structure is a structure that holds all of the queues
    with their corresponding names. It is a meta-queue, essentially. The queues
    class will be a dictionary of dictionaries of jobs, which are
    job names and commands.

    An example command would likely look like:
        cms cc queues list --queues=ab
    """

    def __init__(self, filename=None, database='yamldb'):
        """
        Initializes the giant queue structure.
        Default database is yamldb
        :param name: name of the structure
        :return: creates the queues structure
        """
        if database.lower() == 'yamldb':
            from cloudmesh.cc.db.yamldb.database import Database as QueueDB
            # self.filename = path_expand("~/.cloudmesh/queue/queue")
        elif database.lower() == 'shelve':
            from cloudmesh.cc.db.shelve.database import Database as QueueDB
            # self.filename = path_expand("~/.cloudmesh/queue/queue")
        else:
            raise ValueError("This database is not supported for Queues, please fix.")

        if filename is None:
            self.filename = "~/.cloudmesh/queue/queue"

        if os_is_windows and self.filename.endswith(".dat"):
            try:
                self.fileprefix = self.filename.replace(".dat", "")
            except:
                raise Console.warning(f"On this OS you specified the wrong ending to the filename. You can simply leave it off, or use {prefix}.{ending_for_os})")
        else:
            print("hi")



        self.db = QueueDB(filename=self.filename)

    def save(self):
        """
        save the queue to persistent storage
        """
        self.db.save()

    def load(self):
        self.db.load()

    @property
    def queues(self):
        return self.db.queues

    def add(self, name: str, job:str, command:str):
        """
        Adds a queue to the queues.

        cms cc queues add --queues= abc --queue=d


        :param queue:
        :return: Updates the structure of the queues by addition
        """
        self.db.load()
        self.queues[name][job] = {"name": job, "command": command}
        self.save()

    def create(self, name: str):
        """
        Create a queue

        cms cc queues add --queues= abc --queue=d
        :param queue:
        :return: Updates the structure of the queues by addition
        """

        self.queues[name] = {}
        self.save()


    def remove(self, name):
        """
        removes a queue from the queues

        cms cc queues remove --queues=abc --queue=c

        :param queue:
        :return: updates the structure of the queues by deletion
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
            for queue in self.queues:
                q = self.queues.get(queue)
                print(type(q))
                for job in q:
                    c = q.get(job)
                    r = Shell.run(c)
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
        return str(self.queues)

    @property
    def yaml(self):
        return pyyaml.dump(self.queues, indent=2)

    @property
    def json(self):
        return pyjson.dumps(dict(self.queues), indent=2)
