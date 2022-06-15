from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.cc.data import Data
from cloudmesh.cc.queue import Queue


class CcCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_cc(self, args, arguments):
        """
        ::

          Usage:
                cc upload --data=FILENAME
                cc update --data=FILENAME
                cc delete --data=FILENAME
                cc --queue=QUEUE
                cc add --queue=QUEUE --job=JOB --command=COMMAND
                cc remove --queue=QUEUE --job=JOB
                cc list --queue=QUEUE
                cc run --queue=QUEUE --scheduler=SCHEDULER
                cc start
                cc stop

          This command does some useful things.

          Arguments:
              FILENAME   a file name
              QUEUE  the name of a queue object that has been created
              JOB  the name of a job that has been created
              COMMAND  the command that is associated with the job name
              SCHEDULER  designation of how jobs should be pulled from the queue
              QUEUES  the name of the queues object that has been created

          Options:
              --queue=QUEUE          specify the queue that you want to access
              --data=FILENAME        specify the data that you want to access
              --job=JOB              specify the job name
              --command=COMMAND      specify the command to be added to a job
              --scheduler=SCHEDULER  specify the scheduling technique that is to be used
              --queues=QUEUES        specify the queues object that is to be used

          Description:

            cc start
                start the service

            cc stop
                stop the service


            > cms cc --parameter="a[1-2,5],a10"
            >    example on how to use Parameter.expand. See source code at
            >      https://github.com/cloudmesh/cloudmesh-cc/blob/main/cloudmesh/cc/command/cc.py
            >    prints the expanded parameter as a list
            >    ['a1', 'a2', 'a3', 'a4', 'a5', 'a10']

            > cc exp --experiment=a=b,c=d
            > example on how to use Parameter.arguments_to_dict. See source code at
            >      https://github.com/cloudmesh/cloudmesh-cc/blob/main/cloudmesh/cc/command/cc.py
            > prints the parameter as dict
            >   {'a': 'b', 'c': 'd'}

        """

        # arguments.FILE = arguments['--file'] or None

        # switch debug on

        variables = Variables()
        variables["debug"] = True

        # banner("original arguments", color="RED")

        #VERBOSE(arguments)

        #banner("rewriting arguments so we can use . notation for file, parameter, and experiment", color="RED")

        map_parameters(arguments,
                       "filename",
                       "queue",
                       "job",
                       "command",
                       "scheduler",
                       "queues"
                       )

        #VERBOSE(arguments)

        #banner("rewriting arguments so we convert to appropriate types for easier handeling", color="RED")

        arguments = Parameter.parse(arguments)

        # arguments["queues"] = Parameter.expand(arguments["--queue"])

        #VERBOSE(arguments)

        # banner("showcasing tom simple if parsing based on teh dotdict", color="RED")

        #
        # It is important to keep the programming here to a minimum and any substantial programming ought
        # to be conducted in a separate class outside the command parameter manipulation. If between the
        # elif statement you have more than 10 lines, you may consider putting it in a class that you import
        # here and have propper methods in that class to handle the functionality. See the Manager class for
        # an example.
        #

        if arguments.start:
            print("Start the service")
            raise NotImplementedError

        elif arguments.stop:
            print("Stop the service")
            raise NotImplementedError

        elif arguments.upload and arguments.data:
            filename = arguments.data
            raise NotImplementedError

        elif arguments.update and arguments.data:
            filename = arguments.data

        elif arguments.delete and arguments.data:
            filename = arguments.data

        elif arguments.queue:
            arguments.queue = Queue()

        elif arguments.add and \
                arguments["--queue"] and \
                arguments.job and \
                arguments.command:

            arguments.queue.add(arguments.job, arguments.command)

        elif arguments.remove and \
                arguments.queue and \
                arguments.job:
            arguments.queue.remove(arguments.job)

        elif arguments.run and \
                arguments.queue and \
                arguments.scheduler:
            arguments.queue.run(arguments.scheduler)

        elif arguments.list and arguments.queue:
            arguments.queue.list()

        return ""
