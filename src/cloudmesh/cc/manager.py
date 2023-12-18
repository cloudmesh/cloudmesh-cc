"""Cloudmesh cc manager."""

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.util import path_expand
from builtins import str
import os


class WorkflowCLIManager:
    """Manage the workflow commands given from command line interface."""

    def __init__(self, name: str = None):
        """Initialize the CLI Manager."""
        self.filename = None
        self.filename = None
        self.filename = None
        self.filename = None
        self.name = name

    def add_from_filename(self, filename: str = None):
        """Add a job from a file.

        Handles the command::

            cc workflow add [--name=NAME] [--job=JOB] ARGS...

        Args:
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow()
        filename = path_expand(filename)
        w.load(filename)

    def add_from_arguments(self, job: str = None, filename: str = None, **argv):
        """Add a job.

        Handles the command::

            cc workflow add [--name=NAME] [--job=JOB] ARGS...

        Args:
            job (str): name of job
            filename (str): path to yaml of workflow
            **argv (list): other arguments

        Returns:
            None: nothing
        """
        data = argv
        w = Workflow(filename=filename)
        w.add_job(name=self.name, label=job, **data)

    def delete_job(self, job: str = None):
        """Delete a job.

        Handels the command::

            cc workflow delete [--name=NAME] --job=JOB

        Args:
            job (str): name of job to delete

        Returns:
            None: nothing
        """
        w = Workflow(filename=self.filename)
        w.remove_job(name=job)

    def delete_workflow(self, filename: str = None):
        """Delete a workflow.

        handles the command::

            cc workflow delete [--name=NAME] --job=JOB

        Args:
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        w = Workflow(filename=self.filename)
        w.remove_workflow()

    def list_job(self, job: str = None):
        """List the jobs.

        Handles the command::

            cc workflow list [--name=NAME] [--job=JOB]

        Args:
            job (str): name of job

        Returns:
            None: nothing
        """
        w = Workflow(filename=self.filename)
        j = w.job(name=job)
        print(j)

    def list_workflow(self, filename: str = None):
        """List the workflows.

        Handles the command::

            cc workflow list [--name=NAME] [--filename=FILENAME]

        Args:
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        w = Workflow(filename=filename)
        nodes = w.jobs
        print(nodes)

    def run(self, filename: str = None):
        """Run the workflow.

        Handles the command::

            cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]

        Args:
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        w = Workflow(filename=filename)
        w.run_topo()

    def dependencies(self, name: str = None, dependency: str = None,
                     filename: str = None):
        """Manage the dependencies.

        Handle the command::

            cc workflow NAME DEPENDENCIES

        Args:
            name (str): name of workflow
            dependency (str): name of dependency
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow(filename=filename)
        # I think that the dependencies are separated by commas and will call this function a few times
        w.add_dependencies(dependency=dependency)

    def status_workflow(self, name: str, filename: str = None):
        """Retruns the status of the workflow.

        Handles the command::

            cc workflow status --name=NAME --filename=FILENAME [--output=OUTPUT]

        Args:
            name (str): name of workflow
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow(filename=filename)
        status = w.status()
        print(status)

    def graph(self, filename: str = None):
        """Create a graph from the workflow.

        Handles the command::

            cc workflow graph --name=NAME

        Args:
            filename (str): path to yaml of workflow

        Returns:
            None: nothing
        """
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow(filename=filename)
        graph = w.graph
        print(graph)

