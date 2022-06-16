from cloudmesh.cc.db.yamldb.database import Database as QueueDB
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand

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

    def __init__(self, name=None, command=None):
        self.name = name
        self.command = command

    def __str__(self):
        return f'Job Name= {self.name}, Command={self.command}'


class Queue:
    """
        The queue is data structure that holds the jobs. This means that
        the data structure will be a dictionary because it is holding all of
        names: commands of the jobs. The queue will have several commands:
        instantiate, add, remove, run, get, and list.

        Example of what we expect a command line to look like:

        cms cc queue --queue=a
        cms cc queue add --queue=a --jobname=jobname --command-command
        cms cc queue remove --queue=a --jobname=jobname
        cms cc queue get --queue=a --jobname=jobname
        cms cc queue list --queue=a
        cms cc queue run --queue=a
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
                print(r)
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

    def __init__(self, name):
        """
        Initializes the giant queue structure.

        :param name: name of the structure
        :return: creates the queues structure
        """
        self.name = name
        self.queues = {}
        self.filename = path_expand("~/.cloudmesh/queue/queues.shelve")
        self.db = QueueDB(filename=self.filename)

    def save(self):
        """
        save the queue to persistant storage
        """
        self.db.save()

    def load(self):
        self.queues = self.db.load()
        return self.queues

    def add(self, queue):
        """
        Adds a queue to the queues.

        cms cc queues add --queues= abc --queue=d


        :param queue:
        :return: Updates the structure of the queues by addition
        """
        self.queues[queue.name] = queue.jobs
        self.save()

    def remove(self, queue):
        """
        removes a queue from the queues

        cms cc queues remove --queues=abc --queue=c

        :param queue:
        :return: updates the structure of the queues by deletion
        """
        self.queues.pop(queue)
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


                #self.queues[queue].run(scheduler=scheduler)



        self.save()

    def list(self):
        """
        Returns a list of the queues that are in the queue
        :return:
        """
        for each in self.queues:
            print(each, self.queues[each])

        # no save needed as just list
