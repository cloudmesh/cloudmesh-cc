from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner
from cloudmesh.cc.data import Data
from cloudmesh.cc.Queue import Queue


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
                cc create queue --queue=QUEUE
                cc add --queue=QUEUE --job=JOB --command=COMMAND
                cc remove --queue=QUEUE
                cc run --queue=QUEUE
                cc list --queue=QUEUE

          This command does some useful things.

          Arguments:
              FILENAME   a file name
              NAME  a name is a parameterized set of names
              JOB  the name of a job that has been created
              COMMAND  the command that is associated with the job name

          Options:
              -f      specify the file
              --queue=QUEUE      TBD
              --data=FILENAME    TBD
              --job=JOB         TBD
              --command=COMMAND  TBD

          Description:

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

        # VERBOSE(arguments)

        # banner("rewriting arguments so we can use . notation for file, parameter, and experiment", color="RED")

        map_parameters(arguments,
                       "data",
                       "queues",
                       "queuename",
                       "jobname",
                       "command"
                       )

        # VERBOSE(arguments)

        # banner("rewriting arguments so we convert to appropriate types for easier handeling", color="RED")

        arguments = Parameter.parse(arguments,
                                    data='expand'
                                    )

        # arguments["queues"] = Parameter.expand(arguments["--queue"])

        # VERBOSE(arguments)

        # banner("showcasing tom simple if parsing based on teh dotdict", color="RED")

        #
        # It is important to keep the programming here to a minimum and any substantial programming ought
        # to be conducted in a separate class outside the command parameter manipulation. If between the
        # elif statement you have more than 10 lines, you may consider putting it in a class that you import
        # here and have propper methods in that class to handle the functionality. See the Manager class for
        # an example.
        #

        if arguments.upload and arguments.data:
            filename = arguments.data
        elif arguments.update and arguments.data:
            filename = arguments.data
        elif arguments.delete and arguments.data:
            filename = arguments.data
        elif arguments.create and arguments.queue:
            Queue.create(self,queuename=arguments.queue)
        elif arguments.add and arguments.queue and arguments.job and arguments.command:
            Queue.add(queuename=arguments.queue, jobname=arguments.job,
                      command=arguments.command)
        elif arguments.remove and arguments.queue:
            Queue.remove(queuename=arguments.queue)
        elif arguments.run and arguments.queue:
            Queue.run(queuename=arguments.queue)
        elif arguments.list and arguments.queue:
            Queue.list(queuename=arguments.queue)

        return ""


"""
     if arguments.list and arguments.queuename:
         print('Queue list function')

     elif arguments["--create"] and arguments.create:
         Queue.create(self, queuename=arguments["--queue"])

     elif arguments["--add"] and arguments.add:
         Queue.add(self, queuename=arguments["--queue"], jobname=arguments["--queue"])

     elif arguments["--list"] and arguments.list:
         Queue.create(self, queuename=arguments["--queue"])

     elif arguments["--remove"] and arguments.remove:
         Queue.remove(self, queuename=arguments["--queue"])

     elif arguments["--data"] and arguments.upload:
         Data.upload(self, name=arguments["--data"])

     elif arguments["--data"] and arguments.update:
         Data.update(self, name=arguments["--data"])

     elif arguments["--data"] and arguments.delete:
         Data.delete(self, name=arguments["--data"])

     elif arguments["--queue"] and arguments.list and arguments.job:
         print("jobs")
 """
