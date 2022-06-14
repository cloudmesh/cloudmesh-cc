from queue import Queue as pyQueue
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell


class Job:
    """
        A job is a simply a function that has a command
        We need to queue up these jobs and commands inside an
        array of queued up jobs.
    """

    def __init__(self, queuename, command):
        self.queuename = queuename
        self.command = command

    def __str__(self):
        print('queuename:', self.queuename)
        print('command:', self.command)


class CMQueue:
    """
        Example:
            queues = cmqueue()
            queues.create('localhost')
            queues.add('ls')
            queues.list()
    """

    # initialize the queue object as an array
    def __init__(self):
        self.queue_structure = {}

    # creating the queuename queue
    def create(self, queuename=None):

        # checking the queuename to see what it should be when adding it
        if queuename is not None:
            self.queue_structure[queuename] = Queue()
        else:
            self.queue_structure['localhost'] = Queue()

    def get(self, queuename=None):
        return self.queue_structure[queuename].key()


    # add items to the specified queue
    def add(self, job=None, queuename=None, command=None):
        job = Job(job, command)
        if queuename is not None:
            self.queue_structure[queuename].put(job)
        else:
            self.create(queuename)
            self.queue_structure[queuename].put(job)

    # remove a job in a specified queue
    def remove(self, queuename=None, job=None):
        if queuename is not None and job is not None:
            self.queue_structure[queuename].get(job)
        else:
            Console.error('Cannot remove')



    def run(self, name=None):
        job = self.get(name=name)
        command = job.command
        r = Shell.run(command)

    # figure out in what position a specific job is in the queue
    # def status(self, name):
