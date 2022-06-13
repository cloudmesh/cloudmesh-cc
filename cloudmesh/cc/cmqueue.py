from queue import Queue
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell

class Job:

    def __init__(self, name, command):
        self.name = name
        self.command = command

    def __str__(self):
        print('name:', self.name)
        print('command:', self.command)


class CMQueue:
    """
        Example:
            queues = cmqueue()
            queues.create('localhost')
            queues.add('ls')
            queues.list()
    """

    # initialize the queue object, assuming that this is a FIFO queue.
    def __init__(self):
        self.queue = []

    def create(self, name=None):
        if (name is not None):
            self.name = name
        else:
            self.name='localhost'

        self.queue[name] = Queue()


    # add items to the queue
    def add(self, job=None, name=None, command=None):
        if(name is not None ):
            self.name = name

        job = Job(job, command)
        self.queue[name].put(job)

    # remove the first element of the queue to be started as a job
    def remove(self, name=None, job=None):
        if(name is not None):
            del self.queuesqueues[name]
        elif(job is not None):
            name = self.name or name
            self.queue[name].get(name)
        else:
            Console.error('Cannot remove job')



        self.queue.get(name)

    def get(self, name=None, job=None):
        return self.queues[name][job]


    def run(self, name=None, job=None):
        job = self.get(name=name, job=job)
        command = job.command
        r = Shell.run(command)

    # figure out in what position a specific job is in the queue
    def status(self, name):
        for element in len(self.queue):
            if self.queue[element] == name:
                return "Job is in the", element, "position"

    # list the elements left in the queue
    def list(self):
        for element in len(self.queue):
            print(self.queue[element])