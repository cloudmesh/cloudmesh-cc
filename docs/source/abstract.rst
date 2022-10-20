Extended Abstract
=================

Hybrid Multi-Cloud Analytics Services Framework and Cloudmesh Controlled Computing through Workflows

Gregor von Laszewski (laszewski@gmail.com)\ :math:`^*`, Jacques
Fleischer

:math:`^*` Corresponding author

Background
----------

High-performance computing (HPC) is for decades a very important tool
for science. Scientific applications often consist of multiple
tasks/jobs can be leveraging the processing power of requiring
considerable computational needs. Often a supercomputer is needed to
execute the tasks at high speeds while utilizing the specialized
hardware for acceleration that otherwise are not available to the
user. However, these systems can be difficult to use when conducting
analytic programs that leverage machine learning applied to large data
sets to, for example, predict future values or model current
states. For such highly complex analytics tasks, there are often
multiple steps that need to be run repeatedly either to combine
analytics tasks in competition or cooperation to achieve the best
results. Although leveraging computational GPUs lead to several times
higher performance when applied to deep learning algorithms, may be
not possible at the time as the resources are either too expensive or
simply not available. The analytics task is to simplify this dilemma
and introduce a level of abstraction that focuses on the analytics
task while at the same time allowing sophisticated compute resources
to solve the task for the scientist in the background. Hence, the
scientist should be presented with a function call that automatically
puts together the needed resources and stage the task in jobs on the
HPC environment without the need of too many details of the HPC
environment. Instead, the science user should access analytics REST
services that the user can easily integrate into their scientific code
as functions or services. To facilitate the need to coordinate the
many tasks behind such an abstraction we have developed a specialized
analytics Workflow abstraction and service allowing the execution of
multiple analytics tasks in a parallel workflow, The workflow can be
controlled by the user and is asynchronously executed including the
possibility to utilize multiple HPC computing centers via
user-controlled services.




Workflow Controlled Computing
-----------------------------

The Cloudmesh cc Workflow is enhancing Cloudmesh by integrating an API
and service to make using cloud and HPC resources easier. The
enhancement is focused on a library called Cloudmesh Controlled
Computing (cloudmesh-cc) that adds workflow features to control the
execution of tasks and jobs on remote compute resources including
clouds, desktop computers, and batch-controlled HPC with and without
GPUs. Effectively we access remote, and hybrid resources by
integrating cloud, and on-premise resources.

The goal is to provide an easy way to access these resources, while at
the same time providing the ability to integrate the computational
power enabled through a parallel workflow framework Access to these
complex resources is provided through easy to use interfaces such as a
python API, REST services, and command line tools. Through these
interfaces, the framework is universal and can be integrated into the
science application or other higher level frameworks and even
different programming languages.

The software developed is freely available and can easily be installed
with standard python tools so integration in the python ecosystem
using virtualenv’s and anaconda is simple.



Workflow Functionality
-----------------------

The framework supports workflow functionality to (a) execute workflow
tasks in parallel (b) manage the creation of the workflow by adding
graphs, tasks, and edges (c) control the execution and (d) monitor the
execution The implicit design to access the workflow through an API, a
REST services, and the command line allows easy integration into other
frameworks.


The REST interface is depicted in :numref:`fastapi-service` and is
also available as OpenAPI document.

.. figure:: images/fastapi-service.png
   :alt: Figure OpenAPI Description of the REST Interface to the Workflow
   :name: fastapi-service

   OpenAPI Description of the REST Interface to the Workflow

In addition, the framework supports multiple operating systems like macOS,
Linux, and Windows 10 and 11. This not only includes the ability to run
the workflow on remote computers but also integrates tasks that can be run
locally on the various operating systems to integrate their computational
capabilities. Hence we support easy access to host capabilities, such as
the computer’s localhost, remote computers, and the Linux-based virtual
image WSL. Jobs can be visualized and saved as a YAML and SVG data file.

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
   cd cloudmesh-cc
   pytest -v -x --capture=no tests/test_131_workflow_local.py

This test runs a number of jobs on the local machine
within a singular workflow: the first job runs
a local shell script, the second runs a local Python script, and the
third runs a local Jupyter notebook.


Design
------

The hybrid multi-cloud analytics service framework ensures running
jobs across many platforms. The design includes a small and
streamlined number of abstractions so that jobs and workflows can be
represented easily. This makes it possible to custom design for each
target type a specific job type so that execution on local and remote
compute resources including batch operating systems can be achieved.

Job types for localhost, ssh, SLURM, and WSL are available.  Other job
types can easily be added.  The design is flexible and new job can be
expanded as each job can contain arbitrary arguments. Through this
flexibility jobs types can be also run on different operating systems
including local job on Linux, macOS, Windows 10, and Windows 11, jobs
running in WSL on Windows computers.

An important design requirement to display the dependencies of the
workflow in a direct acyclic Graph is enabled by reusing the Networkx
Graph framework.  This greatly reduced the complexity of the
implementation while being able to leverage graphical displays of the
workflow, as well as implementing sequential execution of workflows as
an alternative to parallel execution while using the build-in
topological sort function.  It serves as an example that custom
schedulers can be designed and easily integrated into the runtime
management while executing the tasks and jobs through a
straightforward interface.  The status of the tasks and jobs is stored
in a file database that can be monitored during program execution. The
creation of the jobs is done prior to the execution of the workflow,
but additional tasks and jobs could be integrated also at
runtime. This is possible when using our parallel scheduler that
selects tasks and jobs once the parent jobs have been completed.  This
is important as it allows dynamic workflow execution of long-running
workflows, while results from previous calculations can be used in
later stages of the workflow and lead to workflow modifications.

We have developed a simple-to-use Python API so programs are easy to
write.  Additionally, we used this API internally to implement a REST
service to deliver a language-independent framework. The obvious
functions to manage workflows are supported including graph
specification through configuration files, upload of workflows,
export, adding jobs and dependencies, and visualizing the workflow
during the execution. An important feature that we added is the
monitoring of the jobs while using progress reports through automated
log file mining. This way each job reports the progress during the
execution. This is also especially important when we run very complex
and long-running jobs.

The REST service was implemented in FastAPI to leverage a small but fast
service that features a much smaller footprint for implementation and
setup in contrast to other similar REST service frameworks using python.



The architectural component building this framework is depicted in
:numref:`workflow-architecture`. The code is available in this
repository and manual pages are provided on how to install it:
`cloudmesh-cc <https://github.com/cloudmesh/cloudmesh-cc>`__.

See :numref:`workflow-architecture` for a diagram of the workflow
components.

.. figure:: images/workflow-architecture.png
   :alt: Figure Design for the workflow.
   :name: workflow-architecture

   The architecture of the Cloudmesh cc Workflow

Additionally, for ease-of-use we have implemented a Graphical User
Interface (GUI) for utilizing the REST service, implemented with
the FastAPI framework in Python. The GUI can be used inside the
internet browser. The GUI features two ways to view the details
of a workflow: the table view and the graph view, both which
contain dynamic, live updating so that a user can view
the status of a workflow as it runs.

See :numref:`workflow-table` for a screenshot of the table view and
:numref:`workflow-graph` for a screenshot of the graph view.

.. figure:: images/service-table.png
   :alt: Table view of a workflow in the browser GUI.
   :name: service-table

   A screenshot of the table view of a workflow in the browser GUI interface

.. figure:: images/service-graph.png
   :alt: Graph view of a workflow in the browser GUI.
   :name: service-graph

   A screenshot of the graph view of a workflow in the browser GUI interface

Application demonstration using MNIST
-------------------------------------

The Modified National Institute of Standards and Technology (MNIST)
Database is large database of handwritten digits. We provide number
example applications using the database. This includes Multilayer
Perceptron, LSTM (Long short-term memory), Auto-Encoder,
Convolutional, and Recurrent Neural Networks, Distributed Training,
and PyTorch training. With Cloudmesh cc we developed a number of
example workflows that run the algorithms on multiple machines.


Summary
-------

We have developed a sophisticated but easy-to-use workflow system
allowing tasks and jobs to be executed on on-premise and remote
machines. Various interfaces exist such as an API, REST service, and
command line tool. With the framework, researchers and scientists
should be able to create jobs on their own, place them in the
workflow, and run them on various types of computers. These jobs can
have analytics functions included and themselves be exposed through an
API, REST service, or command line while hiding the complex setup
needed for collaborating and competing workflow needs accessing
distributed resources.  In addition, developers and users can utilize
the built-in OpenAPI graphical user interface to manage workflows
between jobs. They can be uploaded as YAML files or individually added
through the built-in debug framework.

