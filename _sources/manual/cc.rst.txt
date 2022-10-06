Command cc
==========

::

  Usage:
        cc start [-c] [--reload] [--host=HOST] [--port=PORT]
        cc stop
        cc status
        cc doc
        cc test
        cc workflow add [--name=NAME] [--job=JOB] ARGS...
        cc workflow add [--name=NAME] --filename=FILENAME
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
      JOB  the name of a job that has been created
      COMMAND  the command that is associated with the job name
      SCHEDULER  designation of how jobs should be pulled from the queue

  Options:
      --reload               reload for debugging
      --host=HOST            the host ip [default: 127.0.0.1]
      --port=PORT            the port [default: 8000]
      -c                     flag to set host and port to 0.0.0.0:8000
      --filename=FILENAME    file that contains a workflow specification
      --name=NAME            the workflow name
      --job=JOB              the job name
      --command=COMMAND      a command to be added to a job
      --scheduler=SCHEDULER  the scheduling technique that is to be used

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
    server. In future, we need a mechanism how to set the hostname and port also 
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

    Each workflow can be identified by its name. Note that through 
    cms set workflow=NAME the default name of the workflow can be set. 
    If it is not set the default is `workflow`

    cc workflow service add [--name=NAME] [--directory=DIR] FILENAME
        adds a workflow with the given name from data included in the filename.
        the underlying database will use that name and if not explicitly 
        specified the location of the data base will be  
        ~/.cloudmesh/workflow/NAME/NAME.yaml
        To identify the location a special configuration file will be placed in 
        ~/.cloudmesh/workflow/config.yaml that contains the location of 
        the directories for the named workflows.

    cc workflow service list [--name=NAME] [--job=JOB]
        this command reacts dependent on which options we specify
        If we do not specify anything the workflows will be listed.
        If we specify a workflow name only that workflow will be listed
        If we also specify a job the job will be listed.
        If we only specif the job name, all jobs with that name from all 
        workflows will be returned. # this feature not implemented

    cc workflow service add [--name=NAME] --job=JOB ARGS...
        This command adds a job. with the specified arguments. A check 
        is returned and the user is alerted if arguments are missing
        arguments are passe in ATTRIBUTE=VALUE fashion.
        if the name of the workflow is committed the default workflow is used.
        If no cob name is specified an automated number that is kept in the 
        config.yaml file will be used and the name will be job-n

    cc workflow service delete [--name=NAME] --job=JOB
        deletes the job in the specified workflow

    cc workflow service run [--name=NAME]
        runs the names workflow. If no name is provided the default 
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



