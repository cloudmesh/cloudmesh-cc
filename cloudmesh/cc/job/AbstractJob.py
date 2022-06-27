"""
The Job class creates a simple job that can be executed asynchronously
on a computer. The status of the job is managed through
a number of files that can be quered to identify its execution state.

A job can be created as follows

    job = Job(name=f"job1",
              command="/usr/bin/sleep 120",
              user="user",
              host="host")

it will create an experiment directory where the job specification is
located. To run it, it needs first to be syncronized and copied to the
remote host.

    job.rsync()

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

    def __int__(self, **data):
        pass

    def probe(self):
        """
        gets the error and log files, as well as teh status

        :return:
        :rtype:
        """
        self.get_error()
        self.get_log()
        # state records the last probed status
        self.state = self.status

    def run(self):
        pass

    def get_status(self):
        pass

    def get_error(self):
        pass

    def get_log(self):
        pass

    def sync(self):
        """
        copies the job script into the right location

        :return:
        :rtype:
        """
        pass

    @property
    def status(self):
        return self.get_status()

    def watch(self, period=10):
        """
        watches the status of the job and updates it based on the
        perid specified in seconds

        :param period:
        :type period:
        :return:
        :rtype:
        """