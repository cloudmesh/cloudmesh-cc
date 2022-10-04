"""Abstract job.

The Job class creates a simple job that can be executed asynchronously
on a computer. The status of the job is managed through
a number of files that can be quered to identify its execution state.

A job can be created as follows

    job = Job(name=f"job1",
              command="./test.sh",
              user="user",
              host="host")

it will create an experiment directory where the job specification is
located. To run it, it needs first to be syncronized and copied to the
remote host

    job.sync()

After this we can run it with

    job.run()

Please note the the job runs asynchronously and you can probe its state with

    job.status

Note this is a property and not a function for the user. The final
state is called "end". Users can define their onw states and add them
to the log file so custom actions could be called.

To retrieve the CURRENT log file as a string you can use the functions

    job.get_log()

To retrieve the CURRENT error file as a string you can use the functions

    job.get_error()

To get the pid on the remote machine we can use

    job.pid

Note that prior to running the command job.run(), the variable job.pid has
the value None

"""


class AbstractJob:

    def __init__(self, **argv):
        """
        creates a job by passing either a dict with \*\*dict or named arguments
        attribute1 = value1, ...

        :param data:
        :type data:
        :return:
        :rtype:
        """
        print("argv", argv)
        self.data = dict(argv)
        print("gggggg", self.data)
        # for attribute in self.data:
        #     self[attribute] = self.data[attribute]

    def probe(self):
        """
        gets the error and log files, as well as the status
        and places it localy into

        :return:
        :rtype:
        """
        self.error_file = self.get_error()
        self.log_file = self.get_log()
        # state records the last probed status
        self.state = self.status

        self.error = None  # find error in error file
        self.progress = None  # find last progress in log file

    def run(self):
        pass

    def get_status(self):
        pass

    def get_error(self):
        """returns the content of the error file"""
        pass

    def get_log(self):
        """returns the content of ths stdout file"""
        pass

    def get_progress(self):
        """returns the current progress as reported last in the log file"""
        pass

    def sync(self):
        """
        copies the job script into the right location onto the executing host.

        :return:
        :rtype:
        """
        pass

    @property
    def status(self):
        """
        returns the status of the job as reported in status messages in the
        log file. If additional states need to be defined they can be used as strings
        A status can be followed by a stringified dict, so that more sophisticated
        status messaged can be created::

            # cloudmesh status=ready
            ...
            # cloudmesh status=running {"progress":0, "result": 50}
            ...
            # cloudmesh status=running {"progress": 25, "result": 50}
            ...
            # cloudmesh status=failed
            ...
            # cloudmesh status=done

        :return: returns only the status string. To find other values, use
                 get(attribute)
        :rtype:
        """
        return self.get_status()

    def __getitem__(self, item):
        """
        returns the last value of the given attribute.

        :return:
        :rtype:
        """
        # see status

        return self[item]

    def progress(self):
        return self["progress"]

    def watch(self, period=10):
        """
        watches the status of the job and updates it based on the
        perid specified in seconds

        :param period:
        :type period:
        :return:
        :rtype:
        """
