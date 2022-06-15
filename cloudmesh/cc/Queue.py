from queue import Queue as pyQueue
from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell

class Job:
    """
        A job is a simply a function that has a command
        We need to queue up these jobs and commands inside an
        array of queued up jobs.
    """

    def __init__(self, name, command):
        self.name = name
        self.command = command

    def __str__(self):
        return f'name={self.name}, command={self.command}'

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
    def __init__(self, name):
        """

        Args:
            name ():
        """
        self.name = name
        self.jobs = {}

    def add(self, job):
        """

        Args:
            job ():

        Returns:

        """
        name = job.name
        self.jobs[name] = job

    def get(self, name):
        """

        Args:
            name ():

        Returns:

        """
        if name in self.jobs:
            return self.jobs[name]
        else:
            error = f"job {name} not in queue {self.name}"
            Console.error(error)
            raise ValueError(error)

    def remove(self, name):
        """

        Args:
            name ():

        Returns:

        """
        job = self.get(name)
        del self.jobs[job.name]

    def run(self, scheduler="FIFO"):
        """
        run the jobes in the queue
        Returns:

        """
        raise NotImplementedError
        if scheduler.lower() == "fifo":
            for job in self.jobs:
                print ("Now i run job {job.name} in queue {self.name}")

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

    def remove(self, queuename=None):
        """
        remove a job in a specified queue

        Args:
            queuename ():

        Returns:

        """
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


class Queues:

    def __int__(self):
        queues = {}

    def add(self, queue):
        name = queue.name
        self.queues[name] = queue

    def list(self):
        for queue in self.queues():
            queue.list()
