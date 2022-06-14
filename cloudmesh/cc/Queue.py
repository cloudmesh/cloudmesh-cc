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

        # print('jobname:', self.jobname)
        # print('command:', self.command)


class Queue:
    """
        Example:
            queues = queue()
            queues.create('localhost')
            queues.add('ls')
            queues.list()
    """

    # initialize the queue object as a dictionary
    def __init__(self):
        self.qdict = {}

    def get_job(self, queuename=None):
        qlist = self.qdict[queuename]
        return qlist.get()

    # creating the queuename queue
    def create(self, queuename=None):
        # checking the queuename to see what it should be when adding it
        if queuename is not None:
            self.qdict[queuename] = pyQueue()
        else:
            self.qdict['localhost'] = pyQueue()

    # add items to the specified queue
    def add(self, jobname=None, queuename=None, command=None):
        job = Job(jobname, command)
        if queuename is not None:
            qlist = self.qdict[queuename]
            qlist.put(job)

        else:
            self.create(queuename)
            self.qdict[queuename].put(job)

    # remove a job in a specified queue
    def remove(self, queuename=None):
        if queuename is not None:
            self.qdict[queuename].get()
        else:
            queuename = 'localhost'
            self.qdict[queuename].get()

    def run(self, queuename=None):
        while not self.qdict[queuename].empty():
            j = self.get_job(queuename=queuename)
            r = Shell.run(j.command)
            print(r)


    # list all the elements in a specific queue
    def list(self, queuename):
        print("Queuename:", queuename)
        for i in range(0, self.qdict[queuename].qsize()):
            print(self.qdict[queuename].get(i))
