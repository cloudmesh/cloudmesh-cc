from pprint import pprint

# from cloudmesh.cc.hostdata import Data
from cloudmesh.cc.queue import Queue
from cloudmesh.cc.queue import Queues
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common import banner, VERBOSE
from cloudmesh.common.Shell import Shell
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.variables import Variables
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters


# TODO: these imports needs to be put in where it is needed.
#  It is not supposed to be a global import

from cloudmesh.cc.job.ssh.Job import Job


# if kind == "remote":
#     from cloudmesh.cc.job.ssh.Job import Job
#
# elif kind == "slurm":
#     from cloudmesh.cc.job.slurm.Job import Job
#
# elif kind =="localhost":
#     from cloudmesh.cc.job.local.Job import Job
#
# else:
#     Console.error("kind not supported")

class CcCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_cc(self, args, arguments):
        """
        ::

          Usage:
                cc start [-c] [--reload] [--host=HOST] [--port=PORT]
                cc stop
                cc status
                cc doc
                cc test
                cc workflow add [--name=NAME] [--job=JOB] ARGS...
                cc workflow delete [--name=NAME] [--job=JOB]
                cc workflow list [--name=NAME] [--job=JOB]
                cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
                cc workflow [--name=NAME] --dependencies=DEPENDENCIES
                cc workflow status --name=NAME [--output=OUTPUT]
                cc workflow graph --name=NAME
                cc workflow service add [--name=NAME] FILENAME
                cc workflow service list [--name=NAME] [--job=JOB]
                cc workflow service add [--name=NAME] [--job=JOB] ARGS...
                cc workflow service run --name=NAME

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
              --reload               reload for debugging
              --host=HOST            the host ip [default: 127.0.0.1]
              --port=PORT            the port [default: 8000]
              -c                     flag to set host and port to 0.0.0.0:8000
              --queue=QUEUE          queue that you want to access
              --filename=FILENAME    file that contains a workflow specification
              --name=NAME            the workflow name
              --job=JOB              the job name
              --command=COMMAND      a command to be added to a job
              --scheduler=SCHEDULER  the scheduling technique that is to be used
              --queues=QUEUES        the queues object that is to be used
              
          Description:

            Please note that all arguments such as NAME and JOB can be comma 
            separated parameter expansions, so a command can be applied to multiple
            workflows or jobs at the same time

            
            NEW WORKFLOW CLI COMMANDS
            
            Note that none of the CLI commands use the Workflow service. All actions
            are performed directly in the command shell.
            
            cc workflow add [--name=NAME] [--job=JOB] ARGS...
            cc workflow delete [--name=NAME] --job=JOB
            cc workflow list [--name=NAME] [--job=JOB]
            cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
            cc workflow [--name=NAME] --dependencies=DEPENDENCIES
            cc workflow status --name=NAME [--output=OUTPUT]
            cc workflow graph --name=NAME
            
            NEW WORKFLOW SERVICE COMMANDS
            
            Note that for all service commands to function you need to have a running 
            server. In future, we need a mechnism how to set the hostname and port also 
            for the service commands. For the time being they are issues to 
            127.0.0.1:8000
            
            SERVICE MANAGEMENT COMMANDS
            
            cc start [--reload] [--host=HOST] [--port=PORT]
                start the service.  one can add the host and port so the service is
                started with http://host:port. The default is 127.0.0.1:8000.
                If -c is specified 0.0.0.0:8000 is used. 
                
            cc stop
                stop the service
                Currently this command is not supported.

            cc status
                returns the status of the service
                
            cc doc
                opens a web browser and displays the OpenAPI specification

            cc test
                issues a simple test to see if the service is running. This command
                may be in future eliminated as the status should encompass such a test.
            
            WORKFLOW MANAGEMENT COMMANDS
            
            Each workflow can be identified by its name. Note that thorugh 
            cms set workflow=NAME the default name of the workflow can be set. 
            If it is not set the defualt is `workflow`
            
            cc workflow service add [--name=NAME] [--directory=DIR] FILENAME
                adds a workflow with the given name from data included in the filename.
                the underlaying database will use that name and if not explicitly 
                specified the location of the data base will be  
                ~/.cloudmesh/workflow/NAME/NAME.yaml
                To identify the location a special configuratiion file will be placed in 
                ~/.cloudmesh/workflow/config.yaml that contains the loaction of 
                the directories for the named workflows.
                            
            cc workflow service list [--name=NAME] [--job=JOB]
                this command reacts dependent on which options we specify
                If we do not specify anything the workflows will be listed.
                If we specify a workflow name only that workflow will be listed
                If we also specify a job the job will be listed.
                If we only specif the job name, all jobs with that name from all 
                workflows will be returned.
                            
            cc workflow service add [--name=NAME] --job=JOB ARGS...
                This command ads a job. with the specified arguments. A check 
                is returned and the user is allerted if arguments are missing
                arguments are passe in ATTRIBUT=VALUE fashion.
                if the name of the workflow is ommitted the default workflw is used.
                If no cob name is specified an automated number that is kept in the 
                config.yaml file will be used and the name will be job-n
            
            cc workflow service delete [--name=NAME] --job=JOB
                deletes the job in the specified workflow
                            
            cc workflow service run [--name=NAME]
                runs the names workflow. If no nmae is provided the default 
                workflow is used.

            THIS MAY BE OUTDATED

            cc workflow NAME DEPENDENCIES

               with workflow command you can add dependencies between jobs. The dependencies
               are added to a named workflow. Multiple workflows can be added to create a
               complex workflow.
               The dependency specification is simply a comma separated list of job names
               introducing a direct acyclic graph.

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
               prints the status of the workflow in various formats including
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


        """    # noqa: W605

        # arguments.FILE = arguments['--file'] or None
        # arguments.COMMAND = arguments['--command']

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
                       "reload"
                       )

        # VERBOSE(arguments)

        # banner("rewriting arguments, so we convert to appropriate types for easier handeling", color="RED")

        arguments = Parameter.parse(arguments)

        # arguments["queues"] = Parameter.expand(arguments["--queue"])

        # VERBOSE(arguments)

        # banner("showcasing tom simple if parsing based on teh dotdict", color="RED")

        #
        # It is important to keep the programming here to a minimum and any substantial programming ought
        # to be conducted in a separate class outside the command parameter manipulation. If between the
        # elif statement you have more than 10 lines, you may consider putting it in a class that you import
        # here and have proper methods in that class to handle the functionality. See the Manager class for
        # an example.
        #

        host = arguments["--host"] or "127.0.0.1"
        port = int(arguments["--port"]) or 8000

        if host == "0":
            host = "0.0.0.0"
        if arguments["-c"]:
            host = "0.0.0.0"
            port = 8000

        if arguments.start:
            print("Start the service")
            if arguments.reload:
                reload = True
            else:
                reload = False
            import uvicorn
            from cloudmesh.cc.service.service import app
            r = uvicorn.run(app, host=host, port=port, reload=reload)
            print(r)
        elif arguments.doc:
            url = "http://{host}:{port}}/docs"
            Shell.browser(url)
        elif arguments.test:
            import requests
            url = "http://{host}:{port}}/docs"
            r = requests.get(url)
            pprint(r)
            print(r.text)
        elif arguments.stop:
            print("Stop the service")
            commands = Shell.ps()
            # pprint(commands)
            # print(type(commands))
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

        elif arguments.create and \
                arguments.queues and \
                arguments.database:
            #  cc create --queue=a,b into the correct database: yaml or shelve
            names = Parameter.expand(arguments.queues)
            queues = Queues()
            for name in names:
                queues.create(name)

        #
        # IMPLEMENT THESE
        #

        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        # cc workflow delete [--name=NAME] [--job=JOB]
        # cc workflow list [--name=NAME] [--job=JOB]
        # cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
        # cc workflow [--name=NAME] --dependencies=DEPENDENCIES
        # cc workflow status --name=NAME [--output=OUTPUT]
        # cc workflow graph --name=NAME
        # cc workflow service add [--name=NAME] FILENAME
        # cc workflow service list [--name=NAME] [--job=JOB]
        # cc workflow service job add [--name=NAME] --job=JOB ARGS...
        # cc workflow service run --name=NAME



        """
        #
        # DO NOT IMPLEMENT THESE
        #
        cc donotdofromhereon
        cc future queue create --name=QUEUES --database=DATABASE
        cc future queue add --name=QUEUE --job=JOB --command=COMMAND
        cc future queue run --command=COMMAND
        cc future remove queue --name=QUEUE --job=JOB
        cc future remove queue --name=QUEUE
        cc future list queue --name=QUEUE
                
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

        elif arguments.run and arguments.command:
            # TODO
            print('Here')
            print('woah nelly')
            print(arguments.command)

        elif arguments.list and arguments.queue:
            # TODO: implement with workflow
            q = Queues()
            q.list(self)

        elif arguments.workflow and arguments.NAME and arguments.DEPENDENCIES:

            name = arguments.NAME
            dependencies = Parameter.expand(arguments.DEPENDENCIES)
            workflow = Workflow(name=name, dependencies=dependencies)
            print(workflow)

            # cc workflow NAME DEPENDENCIES
        """

        return ""
