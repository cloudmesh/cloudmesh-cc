from pprint import pprint

# from cloudmesh.cc.hostdata import Data
from cloudmesh.cc.queue import Queue
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Shell import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.cc.queue import Job


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
                cc create --queues=QUEUES --database=DATABASE
                cc add --queue=QUEUE --job=JOB --command=COMMAND
                cc run --queue=QUEUE --scheduler=SCHEDULER
                cc remove --queue=QUEUE --job=JOB
                cc remove --queue=QUEUE
                cc list --queue=QUEUE
                cc start
                cc stop
                cc doc
                cc test
                cc temperature
                cc workflow NAME DEPENDENCIES
                cc workflow status NAME --output=OUTPUT
                cc workflow run NAME
                cc workflow graph NAME


          This command does some useful things.

          Arguments:
              FILENAME   a file name
              QUEUE  the name of the queue object as a variable in code
              QUEUES the name of the queues (dictionary of queues) object
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

            cc workflow NAME DEPENDENCIES

               with workflow command you can add dependencies between jobs. The dependencies
               are added to a named workflow. Multiple workflows can be added to create a
               complex workflow.
               The dependency specification is simply a comma separated list of job names
               introducing a direc acyclic graph.

               > cms cc workflow simple a,b,d
               > cms cc workflow simple a,c,d

               which will introduce a workflow

               >          a
               >        /   \
               >       b     c
               >        \   /
               >          d

            cc workflow run NAME
               runs the workflow with the given name

            cc workflow graph NAME
               creates a graph with the current status. Tasks that have been
               executed will be augmented by metadata, such as runtime

            cc workflow status NAME --output=OUTPUT
               prints the tstatus of the workflow in various formats including
               table, json, yaml

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
                       "filename",
                       "queue",
                       "job",
                       "command",
                       "scheduler",
                       "queues"
                       )

        # VERBOSE(arguments)

        # banner("rewriting arguments so we convert to appropriate types for easier handeling", color="RED")

        arguments = Parameter.parse(arguments)

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

        if arguments.start:
            print("Start the service")

            # command = "uvicorn cloudmesh.cc.service.service:queue_app"
            # os.system(command)
            if True:
                import uvicorn
                from cloudmesh.cc.service.service import app
                r = uvicorn.run(app, host="127.0.0.1", port=8000)
                print(r)
        elif arguments.doc:
            url = "http://127.0.0.1:8000/docs"
            Shell.browser(url)
        elif arguments.test:
            import requests
            url = "http://127.0.0.1:8000/docs"
            r = requests.get(url)
            pprint(r)
            print(r.text)
        elif arguments.temperature:
            url = "http://127.0.0.1:8000/temperature"
            Shell.browser(url)
        elif arguments.stop:
            print("Stop the service")
            commands = Shell.ps()
            #pprint(commands)
            #print(type(commands))
            for command in commands:
                # print(command)
                if command["name"].startswith('python'):
                    cmdline = command["cmdline"]
                    if 'cc' in cmdline and 'start' in cmdline:
                        # print(command)
                        Shell.kill_pid(command["pid"])
                    if 'cloudmesh.cc.service.service:queue_app' in cmdline:
                        # print(command)
                        Shell.kill_pid(command["pid"])


        elif arguments.upload and arguments.data:
            filename = arguments.data
            raise NotImplementedError

        elif arguments.update and arguments.data:
            filename = arguments.data

        elif arguments.delete and arguments.data:
            filename = arguments.data


        elif arguments.create and \
                arguments.queues and \
                arguments.database:
            #  cc create --queue=a,b into the correct database: yaml or shelve
            names = Parameter.expand(arguments.queues)
            queues = Queues()
            for name in names:
                queues.create(name)

        elif arguments.add and \
                arguments.queue and \
                arguments.job and \
                arguments.command:

            # cc add --queue=QUEUE --job=JOB --command=COMMAND
            # here is what the command looks like  cc add --queue=QUEUE --job=JOB --command=COMMAND
            job = arguments.job
            command = arguments.command
            q = Queues()  # how to we access the previously made queue?
            q.add(arguments.queue, job, command)

        elif arguments.remove and arguments.queue:
            q = Queues()
            q.remove(arguments.queue)

        elif arguments.remove and \
                arguments.queue and \
                arguments.job:
            q = Queues()
            q[arguments.queue].remove(arguments.job)

        elif arguments.run and \
                arguments.queue and \
                arguments.scheduler:
            q = Queues()
            q.run(scheduler=arguments.scheduler)

        elif arguments.list and arguments.queue:

            Queue.list(self)


        return ""
