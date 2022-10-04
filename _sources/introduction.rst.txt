What Is Cloudmesh cc?
=====================

Cloudmesh Compute Cluster (cc for short) is a repository
of Python code within the Cloudmesh suite that enables
the creation of workflows. The repository is compatible
with Windows, macOS, and Linux.

Workflows are compilations of jobs to be run on nodes.
These workflows report information on the status of jobs
as they are run, whether locally or remotely. These jobs
can be bash scripts, Python scripts, Jupyter notebooks,
or Slurm scripts. These types of jobs can be mixed with
one another in a single workflow.

The advantage that Cloudmesh cc provides is an interface
to view the progress of a workflow as it is being run in
realtime. The workflow can be monitored as a graph or a
datatable. These interfaces report the statuses of the jobs.
Additionally, the order in which the jobs are run can be
specified, enabling prerequisite jobs and the segmentation
of a workflow.

Cloudmesh cc is bundled with pytests and examples that
can be run on your local machine or on HPC centers such
as UVA's Rivanna supercomputer (authentication is required
for the latter). We encourage you to adapt these tests
to fit your HPC environment.