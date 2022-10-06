from builtins import str

import requests
# when requests is imported, it has its own "str", so we have to import the built-in

class WorkflowServiceManager:
    """Command line interface class for FastAPI service that may be
    deprecated by WorkflowREST. """
    def __init__(self, name=None, port=8000, host="127.0.0.1"):
        self.name = name
        self.host = host
        self.port = port

    def add_job(self, job: str = None, **argv):
        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            name = "workflow"
        if job is None:
            n = 0  # read from config file
            job = f"job-{n}"

        r = requests.post('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass

    def add_from_filename(self, filename=None):

        # resp = requests.post(url=url, files=file)
        # print(resp.json())

        # cc workflow add [--name=NAME] [--job=JOB] ARGS...
        if self.name is None:
            self.name = os.path.basename(filename).replace(".yaml", "")

        # 'https://{self.host}:{self.port}/workflow?name={name}&job={job}'
        url = f'https://{self.host}:{self.port}/workflow'
        file = {'file': open(filename, 'rb')}

        r = requests.post(url=url, files=file)
        print(r.json())

    def delete(self):
        # cc workflow service delete [--name=NAME] --job=JOB
        r = requests.delete('https://{self.host}:{self.port}/workflow?name={name}&job={job}')
        pass

    def list(self, job: str = None):
        # cc workflow service list [--name=NAME] [--job=JOB]
        if self.name is None:
            self.name = "workflow"
        if job is None:
            n = 0
            job = f"job-{n}"

    def status_job(self, name: str = None, job: str = None, output: str = None):
        pass

    def run(self, name: str = None, job: str = None, filename: str = None):
        pass

    def dependencies(self, name: str, dependencies: str = None):
        pass

    def graph(self, name: str):
        pass