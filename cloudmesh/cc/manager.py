from builtins import str

import requests
# when requests is imported, it has it's own "str", so we have to import the built-in
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.util import path_expand
import os

class WorkflowCLIManager:

    def __init__(self, name:str=None):
        self.name = name

    def add_from_filename(self, filename:str=None):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow()
        filename = path_expand(filename)
        w.load(filename)

    def add_from_arguments(self, job:str=None, filename:str=None, **argv):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        data = argv
        w = Workflow(filename=self.filename)
        w.add_job(name=self.name, job=job, **data)

    def  delete_job(self, job:str=None):
        # cc workflow delete [--name=NAME] --job=JOB
        w = Workflow(filename=self.filename)
        w.remove_job(name=job)

    def  delete_workflow(self, workflow:str=None):
        # cc workflow delete [--name=NAME] --job=JOB
        w = Workflow(filename=self.filename)
        w.remove_workflow()

    def  list_job(self, job:str=None):
        # cc workflow list [--name=NAME] [--job=JOB]
        w = Workflow(filename=self.filename)
        j = w.job(name=job)
        print(j)

    def  list_workflow(self, job:str=None, filename:str=None):
        # cc workflow list [--name=NAME] [--filename=FILENAME]
        w = Workflow(filename=filename)
        nodes = w.jobs
        print(nodes)

    def  run (self, str, job:str=None, filename:str=None):
        # cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
        pass

    def dependencies(self, dependencies:str=None):
        # cc workflow [--name=NAME] --dependencies=DEPENDENCIES
        pass

    def  status (self, output:str=None):
        # cc workflow status --name=NAME [--output=OUTPUT]
        pass

    def  graph (self):
        # cc workflow graph --name=NAME
        pass


class WorkflowServiceManager:

    def __init__(self, name=None, port=8000, host="127.0.0.1"):
        self.host = host
        self.port=port

    def add_job(self, name=None, job=None, **argv):
        if name is None:
            name = "workflow"
        if job is None:
            n=0 # read from config file
            job = f"job-{n}"
        r = requests.get('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass

    def add_from_filename(self, filename=None):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        r = requests.get('https://{self.host}:{self.port}/workflow?name={name}&job={job}')


    def delete(self, name=None, str, job=None: str):
        pass


    def list(self, name=None: str, job = None:str):
        pass


    def run(self, name:str=None, job:str=None, filename:str=None):
        pass


    def dependencies(self, name: str, dependencies:str=None):
        pass


    def status(self, name: str, output:str=None):
        pass


    def graph(self, name: str):
        pass