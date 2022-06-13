from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner

class CcCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_cc(self, args, arguments):
        """
        ::

          Usage:
                cc upload --data=FILENAME
                cc queue create NAME
                cc queue delete NAME
                cc queue add [--queue=NAME] JOB
                cc queue set NAME
                cc queue run JOB
                cc queue list [--queue=QUEUES]
                cc queue list [--job=JOBS]

          This command does some useful things.

          Arguments:
              FILE   a file name
              PARAMETER  a parameterized parameter of the form "a[0-3],a5"

          Options:
              -f      specify the file
              --queue=QUEUES  TBD
              --job=JOBS      TBD

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

        banner("original arguments", color="RED")

        VERBOSE(arguments)

        banner("rewriting arguments so we can use . notation for file, parameter, and experiment", color="RED")

        map_parameters(arguments,
                       "job",
                       "data")

        VERBOSE(arguments)

        banner("rewriting arguments so we convert to appropriate types for easier handeling", color="RED")

        arguments = Parameter.parse(arguments,
                                    job='expand',
                                    data='expand')

        arguments["queues"] = Parameter.expand(arguments["--queue"])



        VERBOSE(arguments)

        banner("showcasing tom simple if parsing based on teh dotdict", color="RED")

        #
        # It is important to keep the programming here to a minimum and any substantial programming ought
        # to be conducted in a separate class outside the command parameter manipulation. If between the
        # elif statement you have more than 10 lines, you may consider putting it in a class that you import
        # here and have propper methods in that class to handle the functionality. See the Manager class for
        # an example.
        #

        if arguments.queue and arguments.set:

            q = arguments["--queue"]
            print(f"print set {q}")

        elif arguments["--queue"] and arguments.list and arguments.job:
            print("jobs")

        return ""
