class WorkflowCLIManager:

    def __init__(self, name=None:str):
        pass

    def add(self, name=None, str, job=None:str, **argv):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        pass

    def  delete (self, name=None, str, job=None:str):
        # cc workflow delete [--name=NAME] --job=JOB
        pass

    def  list (self, name=None: str, job=None:str):
        # cc workflow list [--name=NAME] [--job=JOB]
        pass

    def  run (self, name=None: str, job=None:str, filename=None: str):
        # cc workflow run [--name=NAME] [--job=JOB] [--filename=FILENAME]
        pass

    def dependencies(self, name:str, dependencies=None: str):
        # cc workflow [--name=NAME] --dependencies=DEPENDENCIES
        pass

    def  status (self, name:str, output=None: str):
        # cc workflow status --name=NAME [--output=OUTPUT]
        pass

    def  graph (self, name:str):
        # cc workflow graph --name=NAME


class WorkflowServiceManager:

    def __init__(self, name=None: str):
        pass


    def add(self, name=None, str, job=None: str, ** argv):
        pass


    def delete(self, name=None, str, job=None: str):
        pass


    def list(self, name=None: str, job = None:str):
        pass


    def run(self, name=None: str, job = None:str, filename = None: str):
        pass


    def dependencies(self, name: str, dependencies=None: str):
        pass


    def status(self, name: str, output=None: str):
        pass


    def graph(self, name: str):
        pass