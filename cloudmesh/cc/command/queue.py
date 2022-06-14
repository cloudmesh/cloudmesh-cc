from queue import Queue as pyQueue
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell


class Job:
    """
        A job is a simply a function that has a command
        We need to queue up these jobs and commands inside an
        array of queued up jobs.
    """

    def __init__(self, jobname, command):
        self.jobname = jobname
        self.command = command

    def __str__(self):
        return f'{self.jobname}, Command- {self.command}'

        #print('jobname:', self.jobname)
        #print('command:', self.command)


class Queue:
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
            self.queue_structure[queuename] = pyQueue()
        else:
            self.queue_structure['localhost'] = pyQueue()

    def grab(self, queuename=None):
        return self.queue_structure[queuename].key()

    # add items to the specified queue
    def add(self, jobname=None, queuename=None, command=None):
        job = Job(jobname, command)
        if queuename is None:
            self.create(queuename)
            self.queue_structure[queuename].put(job)
        else:
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

    # list all the elements in a specific queue
    def list(self, queuename):
        for i in range(0, self.queue_structure[queuename].qsize()):
            print(self.queue_structure[queuename].get(i))






