Extended Abstract
=================

Hybrid Multi-Cloud Analytics Services Framework and Cloudmesh Controlled Computing through Workflows

Gregor von Laszewski (laszewski@gmail.com)\ :math:`^*`, Jacques
Fleischer

:math:`^*` Corresponding author

Background
----------

High-performance computing (HPC) is for decades a very important tool
for science. Scientific applications often consist of multiple tasks
tasks can be leveraging the processing power of requiring considerable
computational needs. Often a supercomputer is needed to execute
the tasks at high speeds while
utilizing the specialized hardware for acceleration that otherwise are not
available to the user. However, these systems can be difficult to use when conducting
analytic programs that
leverage machine learning applied to large data sets to, for example,
predict future values or model current states. For such
highly complex analytics tasks, there are often multiple steps that
need to be run repeatedly either to combine analytics tasks in competition
or cooperation to achieve the best results. Although leveraging
computational GPUs lead to several times higher performance when applied to
deep learning algorithms, may be not possible at the time as the resources are
either too expensive or simply not available. The analytics task is to simplify
this dilemma and introduce a level of abstraction that focuses on the
analytics task while at the same time allowing sophisticated compute resources to
solve the task for the scientist in the background. Hence, the scientist should be
presented with a function call that automatically puts together the needed resources
and stage the jobs on the HPC environment without the need of too many details of
the HPC environment. Instead, the science user should access
analytics REST services that the user can easily integrate into their
scientific code as functions or services. To facilitate the need to coordinate
the many tasks behind such an abstraction we have developed a specialized analytics
Workflow abstraction and service allowing the execution of multiple analytics tasks
in a parallel workflow, The workflow can be controlled by the user and is
asynchronously executed including the possibility to utilize multiple HPC
computing centers via user-controlled services.



See :numref:`fastapi-service` for the OpenAPI interface of such service.

.. figure:: images/fastapi-service.png
   :alt: Figure OpenAPI Description of the REST Interface to the Workflow
   :name: fastapi-service

   OpenAPI Description of the REST Interface to the Workflow

Workflow Controlled Computing
-----------------------------

The Cloudmesh cc Workflow is enhancing Cloudmesh by integrating an API and service to
make using cloud and HPC resources easier. The enhancement is focused on
a library called Cloudmesh Controlled Computing (cloudmesh-cc)
that adds workflow features to control the execution of jobs on remote
compute resources including clouds, desktop computers, and batch-controlled HPC with
and without GPUs. Effectively we access remote, and hybrid resources by integrating cloud,
 and on-premise resources.

The goal is to provide an easy way to access these resources, while at the same time providing
the ability to integrate the computational power enabled through a
parallel workflow framework  Access to these complex resources is provided through easy to use
interfaces such as a python API, REST services, and command line tools. Through these interfaces, the framework is universal and can be integrated into the science application or other higher level
frameworks and even different programming languages.

The software developed is freely available and can easily be installed
with standard python tools so integration in the python ecosystem using
virtualenv’s and anaconda is simple.


Workflow Functionality
----------------------

The framwork supports workflow functionality to (a) execute workflow tasks
in parralel (b) manage the creation of the workflow by adding graphs, tasks, and edges
(c) controll the execution and (d) monitor the execution
The impcit design to
access the workflow through an API, a REST services, and the commandline
allows easy integration into other frameworks.

 In addition, the framework
supports multiple operating systems like macOS, Linux, and Windows 10
and 11. This not only includes the ability to run the workflow on remote
computers, but also integrate tasks that can be run locally on the
various operating systems to integrate their computational capabilities.
Hence we support easy acces to host capabilities, such as the computer’s localhost, remote computers,
and the Linux-based virtual image WSL. Jobs can be visualized and saved
as a YAML and SVG data file.

Quickstart
----------

To utilize the workflow program, prepare a cm directory in your home
directory by executing the following commands in a terminal:

.. code:: bash

   cd ~
   mkdir cm
   cd cm
   pip install cloudmesh-installer -U
   cloudmesh-installer get cc
   git clone https://github.com/cloudmesh/cloudmesh-cc
   cd cloudmesh-cc
   pip install -e .
   pip install -r requirements.txt
   pytest -v -x --capture=no tests/test_131_workflow_local.py

This test runs a number of jobs on the local machine
within a singular workflow: the first job runs
a local shell script, the second runs a local Python script, and the
third runs a local Jupyter notebook.

Application demonstration using MNIST
-------------------------------------

The Modified National Institute of Standards and Technology Database is
a machine learning database based on image processing Various MNIST
files involving different machine learning cases were modified and
tested on various local and remote machines These cases include
Multilayer Perceptron, LSTM (Long short-term memory), Auto-Encoder,
Convolutional, and Recurrent Neural Networks, Distributed Training, and
PyTorch training

See :numref:`workflow-uml` for a diagram of the workflow components.

.. figure:: images/workflow-uml.png
   :alt: Figure Design for the workflow.
   :name: workflow-uml

   Design for the workflow.

Design
------

The hybrid multi-cloud analytics service framework was created to ensure
running jobs across many platforms. We designed a small and streamlined
number of abstractions so that jobs and workflows can be represented
easily. The design is flexible and can be expanded as each job can
contain arbitrary arguments. This made it possible to custom design for
each target type a specific job type so that execution on local and
remote compute resources including batch operating systems can be
achieved. The job types supported include: local job on Linux, macOS,
Windows 10, and Windows 11, jobs running in WSL on Windows computers,
remote jobs using SSH, and batch jobs using Slurm.

In addition, we leveraged the exiting Networkx Graph framework to allow
dependencies between jobs. This greatly reduced the complexity of the
implementation while being able to leverage graphical displays of the
workflow, as well as using scheduling jobs with for example topological
sort available in Networkx. Custom schedulers can be designed easily
based on the dependencies and job types managed through this
straightforward interface. The status of the jobs is stored in a
database that can be monitored during program execution. The creation of
the jobs is done on the fly, e.g. when the job is needed to be
determined on the dependencies when all its parents are resolved. This
is especially important as it allows dynamic workflow patterns to be
implemented while results from previous calculations can be used in
later stages of the workflow.

We have developed a simple-to-use API for this so programs can be
formulated using the API in python. However, we embedded this API also
in a prototype REST service to showcase that integration into
language-independent frameworks is possible. The obvious functions to
manage workflows are supported including graph specification through
configuration files, upload of workflows, export, adding jobs and
dependencies, and visualizing the workflow during the execution. An
important feature that we added is the monitoring of the jobs while
using progress reports through automated log file mining. This way each
job reports the progress during the execution. This is especially of
importance when we run very complex and long-running jobs.

The REST service was implemented in FastAPI to leverage a small but fast
service that features a much smaller footprint for implementation and
setup in contrast to other similar REST service frameworks using python.

The architectural component building this framework is depicted in
:numref:`workflow-uml`. The code is available in this repository and
manual pages are provided on how to install it:
`cloudmesh-cc <https://github.com/cloudmesh/cloudmesh-cc>`__.

Summary
-------

The main interaction with the workflow is through the command line. With
the framework, researchers and scientists should be able to create jobs
on their own, place them in the workflow, and run them on various types
of computers.

In addition, developers and users can utilize the built-in OpenAPI
graphical user interface to manage workflows between jobs. They can be
uploaded as YAML files or individually added through the build-in debug
framework.

Improvements to this project will include code cleanup and manual
development.

