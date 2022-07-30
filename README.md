# Hybrid Multi-Cloud Analytics Services Framework

Cloudmesh Controlled Computing through Workflows

Gregor von Laszewski (laszewski@gmail.com)$^*$,
Jaques Fleischer,
Jakson Miskill,
Alision Liu,
Alex Beck

$^*$ Corresponding author, University of Virginia

## References

An older version of the poster is avalable as pptx and PDF file. However, that version is no longer valid and is superseeded by this document.

* [Poster Presentation (PPTX)](https://github.com/cloudmesh/cloudmesh-cc/raw/main/documents/analytics-service.pptx)
* [Poster Presentation (PDF)](https://github.com/cloudmesh/cloudmesh-cc/raw/main/documents/analytics-service.pdf)

## Background

High performance computing (HPC) is for decades a very important
tool for science. Scientific tasks can be leveraging the processing power of a supercomputer so they can can
run at previously unobtainable high speeds or utilize specialized hardware for acceleration that otherwise are not available to the user. HPC can be used for
analytic programs that leverage  machine learning applied to large data sets to,
for example, predict future values or to model current states. For such
high-complexity projects, there are often multiple complex programs
that may be ran reppeatedly in either competition or cooperation. Leveraging for example computational GPUs
leads to several times higher performancewhen applied to deep
learning algorithms. With such projects, program execution is
submitted as a job to a typically remote HPC centers
such as UVA's Rivanna, where time is billed as node-hours. It is
necessary for such projects to have a service that lets the user
manage and execute without supervision. We have created a service that
lets the user run jobs across multiple platforms in a dynamic queue
with visualization and data storage.

![OpenAPI Description of the REST Interface to the Workflow](images/fastapi-service.png){#fig:fastapi-service width=50%}


## Workflow Controlled Computing

This software was developed end enhancing Cloudmesh, a suite of software to make usig cloud and HPC resources easier. Specifically we have added 
a library called Cloudmesh Controled Computing (cloudmesh-cc) that adds workflow features to controll the execution of jobs on remote compute resoources.

The goal is to provides numerous methods of specifying the workflows on a local computer and running them on remote services such as HPC and cloud computing resources. This includes REST services and commandline tools. The softeare developed is freely available and can easily be installed with standard pythin tools so integration in the python ecosystem using virtualenvs and conda is simple.


## Workflow Functionality

A hybrid multi-cloud analytics service framework was created to manage
heterogeneous and remote workflows, queues, and jobs.  It was designed
for access through both the command line and REST services
to simplify the coordination of tasks on remote computers.  In
addition, this service supports multiple operating systems like MacOS,
Linux, and Windows 10 and 11, on various hosts: the computer's
localhost, remote computers, and the Linux-based virtual image WSL.
Jobs can be visualized and saved as a YAML and SVG data file. This
workflow was extensively tested for functionality and reproducibility.

## Application demonstration using MNIST

The Modified National Institute of Standards and Technology Database
is a machine learning database based on image processing Various MNIST
files involving different machine learning cases were modified and
tested on various local and remote machines These cases include
Multilayer Perceptron, LSTM (Long short-term
memory), Auto-Encoder, Convolutional and Recurrent Neural
Networks, Distributed Training, and PyTorch training

![Design for the workflow.](images/workflow-uml.png){#fig:workflow-uml}

## Design

The hybrid multi-cloud analytics service framework was
created to ensure running jobs across
many platforms. We designed a small and streamlined number of abstractions so that jobs and workflows can be represented easily. The diesign is flexible and can be expanded as ech job can contain arbitrary arguments. This made it possible to custom design for each target type a specific job type so that execution on local and remote compute resources including batch operating systems can be achieved. The job types supported include:
local job on Linux, macOS, Windows 10, WIndows 11, jobs running in WSL on Windows compputers, remote jibs using ssh, and a batch JObs using Slurm.



In addition we leveraged the exiting Networkx Graph framework to allow dependencies between jobs. This greatly reduced the complexity of the implementation while being able to leverage graohical displays of the workflow, as well as using scheduling jobs with for example topological sort available in Networkx. Custom schedulers chan be designed easily based on a the dependencies and job types managed through this straight forward interface. The status of the jobs are stored in a database that can be monitored during program execution. The creation of the jobs is done on the fly, e.g. when the job is needed determined on the dependencies when all its parents are resolved. THis is especially important as it allows dynamic workflow patterns to be implemented while results from previous calculations can be used in later stages of the workflow. 

We have developed a simpel to use API for this so programs can be formulated using the API in pythin. HOwever, we embedded this API also in a prototype REST service to showcase that integration into language independent frameworks is possible. The obvious functions to manage workflows are supported including graph specification throug configuration files, upload of workflows, export, adding jobs and dependencies, visualizing the workflow during the execution. AN important feature that we added is the monitoring of the jobs while using progress reports through automated log file minining. This way each job reports the progress during the execution. This is esppecially of importance when we run very complex and long running jobs.


The REST ervice was implemented in FastAPI to leverage a small but fast serfvice which features a much smaller footprint for implementation and setup in contrast to other similar REST service frameworks using python.

This architectural componenst building thid framework ars depicted  @fig:workflow-uml.
The code is availabe in this repository and manual pages are provided how to install it:
[cloudmesh-cc](https://github.com/cloudmesh/cloudmesh-c).

## Summary

The main interaction with the workflow is through the commandline.
With theframework, researchers and scientists should be able to
create jobs on their own, place them in the workflow, and run them on
various types of computers.

In addition, developers and userscan utilize the build in OpenAPI 
graphical user interface to manage
workflows between jobs. They can be uploaded as yaml files or individually 
added through the build in debug framework.

Improvements to this project will include code cleanup and manaul development.

