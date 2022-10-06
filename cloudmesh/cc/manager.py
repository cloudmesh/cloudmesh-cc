"""Cloudmesh cc manager."""

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.util import path_expand
from builtins import str
import os


class WorkflowCLIManager:
    """Class that handles the workflow commands given from command line
    interface."""
    def __init__(self, name: str = None):
        self.filename = None
        self.filename = None
        self.filename = None
        self.filename = None
        self.name = name

    def add_from_filename(self, filename: str = None):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow()
        filename = path_expand(filename)
        w.load(filename)

    def add_from_arguments(self, job: str = None, filename: str = None, **argv):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        data = argv
        w = Workflow(filename=filename)
        w.add_job(name=self.name, label=job, **data)

    def delete_job(self, job: str = None):
        # cc workflow delete [--name=NAME] --job=JOB
        w = Workflow(filename=self.filename)
        w.remove_job(name=job)

    def delete_workflow(self, filename: str = None):
        # cc workflow delete [--name=NAME] --job=JOB
        w = Workflow(filename=self.filename)
        w.remove_workflow()

    def list_job(self, job: str = None):
        # cc workflow list [--name=NAME] [--job=JOB]
        w = Workflow(filename=self.filename)
        j = w.job(name=job)
        print(j)

    def list_workflow(self, filename: str = None):
        # cc workflow list [--name=NAME] [--filename=FILENAME]
        w = Workflow(filename=filename)
        nodes = w.jobs
        print(nodes)

    def run(self, job: str = None, filename: str = None):
        # cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
        w = Workflow(filename=filename)
        w.run_parallel()

    def dependencies(self, name: str = None, dependency: str = None,
                     filename: str = None):
        # cc workflow NAME DEPENDENCIES
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow(filename=filename)
        # I think that the dependencies are separated by commas and will call this function a few times
        w.add_dependencies(dependency=dependency)

    def status_workflow(self, name: str, filename: str = None,
                        output: str = None):
        # cc workflow status --name=NAME --filename=FILENAME [--output=OUTPUT]
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow(filename=filename)
        status = w.status()
        print(status)

    def graph(self, filename: str = None):
        # cc workflow graph --name=NAME
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow(filename=filename)
        graph = w.graph
        print(graph)

