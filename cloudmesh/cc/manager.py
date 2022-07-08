import requests
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.util import path_expand
from builtins import str
import os

class WorkflowCLIManager:

    def __init__(self, name:str=None):
        self.name = name


    def add_from_filename(self, filename=None):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        w = Workflow()
        filename = path_expand(filename)
        w.load(filename)

    def add_from_arguments(self, str, job=None:str, **argv):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        w = Workflow()
        w.load("tests/workflow.yaml")

        pass

    def  delete (self, str, job=None:str):
        # cc workflow delete [--name=NAME] --job=JOB
        pass

    def  list (self, job=None:str):
        # cc workflow list [--name=NAME] [--job=JOB]
        pass

    def  run (self, str, job=None:str, filename=None: str):
        # cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
        pass

    def dependencies(self,  dependencies=None:str):
        # cc workflow [--name=NAME] --dependencies=DEPENDENCIES
        pass

    def  status (self, output=None:str):
        # cc workflow status --name=NAME [--output=OUTPUT]
        pass

    def  graph (self):
        # cc workflow graph --name=NAME
        pass


class WorkflowServiceManager:

    def __init__(self, name=None, port=8000, host="127.0.0.1"):
        self.name = name
        self.host = host
        self.port=port

    def add_job(self, job:str=None, **argv):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            name = "workflow"
        if job is None:
            n=0 # read from config file
            job = f"job-{n}"
        r = requests.post('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass

    def add_from_filename(self, filename:str=None):
        # cc workflow service add [--name=NAME] [--directory=DIR] FILENAME
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")
        r = requests.post('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass


    def delete(self):
        # cc workflow service delete [--name=NAME] --job=JOB
        r = requests.delete('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass


    def list(self, job:str=None):
        # cc workflow service list [--name=NAME] [--job=JOB]
        if self.name is None:
            self.name = "workflow"
        if job is None:
            n=0
            job = f"job-{n}"
        r = requests.get('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass


    def run(self, filename:str= None):
        # cc workflow service run [--name=NAME]
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")
        r = requests.get('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass


    def dependencies(self, name:str=None, dependencies=None):
        # cc workflow NAME DEPENDENCIES
        pass

    def status_workflow(self, name: str, output=None: str):
        pass


    def status_job(self, name:str=None, job:str=None, output=None: str):
        pass


    def graph(self, name: str):
        pass