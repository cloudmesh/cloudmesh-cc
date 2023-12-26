# Hybrid Multi-Cloud Analytics Services Framework

**Cloudmesh Controlled Computing through Workflows**

Gregor von Laszewski (laszewski@gmail.com)$^*$,
Jacques Fleischer

$^*$ Corresponding author

## Citation

* <https://arxiv.org/pdf/2210.16941>
*  <https://github.com/cyberaide/paper-cloudmesh-cc/raw/main/vonLaszewski-cloudmesh-cc.pdf>

```
@misc{las-2022-hybrid-cc,
  title =	 {Hybrid Reusable Computational Analytics Workflow
                  Management with Cloudmesh},
  author =	 {Gregor von Laszewski and J. P. Fleischer and
                  Geoffrey C. Fox},
  year =	 2022,
  eprint =	 {2210.16941},
  archivePrefix ={arXiv},
  primaryClass = {cs.DC},
  url =		 {https://arxiv.org/pdf/2210.16941},
  urlOPT =
                  {https://github.com/cyberaide/paper-cloudmesh-cc/raw/main/vonLaszewski-cloudmesh-cc.pdf}
}
```


## Background

High-performance computing (HPC) is for decades a very important tool
for science. Scientific tasks can be leveraging the processing power
of a supercomputer so they can run at previously unobtainable high
speeds or utilize specialized hardware for acceleration that otherwise
are not available to the user. HPC can be used for analytic programs
that leverage machine learning applied to large data sets to, for
example, predict future values or to model current states. For such
high-complexity projects, there are often multiple complex programs
that may be running repeatedly in either competition or
cooperation. Leveraging for example computational GPUs leads to
several times higher performance when applied to deep learning
algorithms. With such projects, program execution is submitted as a
job to a typically remote HPC center, where time is billed as node
hours. Such projects must have a service that lets the user manage and
execute without supervision. We have created a service that lets the
user run jobs across multiple platforms in a dynamic queue with
visualization and data storage.

See @fig:fastapi-service.

![OpenAPI Description of the REST Interface to the Workflow](images/fastapi-service.png){#fig:fastapi-service width=50%}


## Workflow Controlled Computing

This software was developed end enhancing Cloudmesh, a suite of
software to make using cloud and HPC resources easier. Specifically,
we have added a library called Cloudmesh Controlled Computing
(cloudmesh-cc) that adds workflow features to control the execution of
jobs on remote compute resources.

The goal is to provide numerous methods of specifying the workflows on
a local computer and running them on remote services such as HPC and
cloud computing resources. This includes REST services and command
line tools. The software developed is freely available and can easily
be installed with standard Python tools so integration in the Python
ecosystem using virtualenv's and Anaconda is simple.


## Workflow Functionality

A hybrid multi-cloud analytics service framework was created to manage
heterogeneous and remote workflows, queues, and jobs. It was designed
for access through both the command line and REST services
to simplify the coordination of tasks on remote computers. In
addition, this service supports multiple operating systems like macOS,
Linux, and Windows 10 and 11, on various hosts: the computer's
localhost, remote computers, and the Linux-based virtual image WSL.
Jobs can be visualized and saved as a YAML and SVG data file. This
workflow was extensively tested for functionality and reproducibility.

## Quickstart

To test the workflow program, prepare a cm directory in your home
directory by executing the following commands in a terminal:

```bash
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
cd cloudmesh-cc
pytest -v -x --capture=no tests/test_199_workflow_clean.py
```

This test runs three jobs within a singular workflow: the first job
runs a local shell script, the second runs a local Python script, and
the third runs a local Jupyter notebook.

## Application demonstration using MNIST

The Modified National Institute of Standards and Technology Database
is a machine learning database based on image processing Various MNIST
files involving different machine learning cases were modified and
tested on various local and remote machines These cases include
Multilayer Perceptron, LSTM (Long short-term memory), Auto-Encoder,
Convolutional, and Recurrent Neural Networks, Distributed Training,
and PyTorch training.

See @fig:workflow-uml.

![Design for the workflow.](images/workflow-uml.png){#fig:workflow-uml}

## Design

The hybrid multi-cloud analytics service framework was created to
ensure running jobs across many platforms. We designed a small and
streamlined number of abstractions so that jobs and workflows can be
represented easily. The design is flexible and can be expanded as each
job can contain arbitrary arguments. This made it possible to custom
design for each target type a specific job type so that execution on
local and remote compute resources including batch operating systems
can be achieved. The job types supported include: local job on Linux,
macOS, Windows 10, and Windows 11, jobs running in WSL on Windows
computers, remote jobs using ssh, and batch jobs using Slurm.



In addition, we leveraged the existing Networkx Graph framework to
allow dependencies between jobs. This greatly reduced the complexity
of the implementation while being able to leverage graphical displays
of the workflow, as well as using scheduling jobs with for example
topological sort available in Networkx. Custom schedulers can be
designed easily based on the dependencies and job types managed
through this straightforward interface. The status of the jobs is
stored in a database that can be monitored during program
execution. The creation of the jobs is done on the fly, e.g. when the
job is needed to be determined on the dependencies when all its
parents are resolved. This is especially important as it allows
dynamic workflow patterns to be implemented while results from
previous calculations can be used in later stages of the workflow.

We have developed a simple-to-use API for this so programs can be
formulated using the API in Python. However, we embedded this API also
in a prototype REST service to showcase that integration into
language-independent frameworks is possible. The obvious functions to
manage workflows are supported including graph specification through
configuration files, upload of workflows, export, adding jobs and
dependencies, and visualizing the workflow during the execution. An
important feature that we added is the monitoring of the jobs while
using progress reports through automated log file mining. This way
each job reports the progress during the execution. This is especially
of importance when we run very complex and long-running jobs.


The REST service was implemented in FastAPI to leverage a small but
fast service that features a much smaller footprint for implementation
and setup in contrast to other similar REST service frameworks using
python.

This architectural component building this framework is depicted
@fig:workflow-uml.  The code is available in this repository and
manual pages are provided on how to install it:
[cloudmesh-cc](https://github.com/cloudmesh/cloudmesh-cc).

## Summary

The main interaction with the workflow is through the command line.
With the framework, researchers and scientists should be able to
create jobs on their own, place them in the workflow, and run them on
various types of computers.

In addition, developers and users can utilize the built-in OpenAPI 
graphical user interface to manage
workflows between jobs. They can be uploaded as YAML files or individually 
added through the build-in debug framework.

Improvements to this project will include code cleanup and manual development.

## References

A poster based on a pre-alpha version of this code is available as ppt
and PDF file. However, that version is no longer valid and is
superseded by much improved efforts. The code summarized in the
pre-alpha version was mainly used to teach a number of students Python
and how to work in a team

* [Poster Presentation (PPTX)](https://github.com/cloudmesh/cloudmesh-cc/raw/main/documents/analytics-service.pptx)
* [Poster Presentation (PDF)](https://github.com/cloudmesh/cloudmesh-cc/raw/main/documents/analytics-service.pdf)

Please note also that the poster contains inaccurate statements and
descriptions and should not be used as a reference to this work.

## Acknowledgments

Continued work was in part funded by the NSF CyberTraining: CIC:
CyberTraining for Students and Technologies from Generation Z with the
award numbers 1829704 and 2200409.
We like to thank the following contributors for their help and evaluation in a 
pre-alpha version of the code: Jackson Miskill, Alex Beck, Alison Lu.
We are excited that this effort contributed significantly to their
increased understanding of Python and how to develop in a team using
the Python ecosystem.

## Manual Page

<!-- START-MANUAL -->
```
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


```
<!-- STOP-MANUAL -->