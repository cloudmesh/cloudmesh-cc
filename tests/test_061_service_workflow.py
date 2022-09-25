###############################################################
# pytest -v --capture=no tests/test_061_service_workflow.py
# pytest -v  tests/test_061_service_workflow.py
# pytest -v --capture=no  tests/test_061_service_workflow.py::TestService::<METHODNAME>
###############################################################
import glob
from pathlib import Path

import os
import time
import yaml
import json
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient


from cloudmesh.cc.service.service import app
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import readfile
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Console, Shell
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.variables import Variables
from cloudmesh.common.systeminfo import os_is_windows
from utilities import set_host_user
from utilities import create_dest, create_workflow_service

create_dest()

banner(Path(__file__).name, c = "#", color="RED")


client = TestClient(app)

variables = Variables()

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

username = variables["username"]

if username is None:
    Console.error("No username provided. Use cms set username=ComputingID")
    quit()

w = None

def create_workflow(filename="workflow-service.yaml"):
    global w
    global username

    create_workflow_service()
    w = Workflow(filename=filename, load=False)

    localuser = Shell.sys_user()
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"},
        "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
        "pi": {"user": f"{localuser}", "host": "red"},
    }

    n = 0

    user = login["localhost"]["user"]
    host = login["localhost"]["host"]

    jobkind="local"

    shell_files = Path(f'{__file__}').as_posix()
    shell_files_dir = Path(os.file.dirname(shell_files)).as_posix()
    runtime_dir = Path(Shell.map_filename(
        '~/.cloudmesh/workflow/workflow-service/runtime').path).as_posix()
    # Shell.mkdir('./runtime')
    # os.chdir('./runtime')
    for script in ["start", "job-local-0", "job-local-1", "job-local-2",
                   "job-rivanna.hpc.virginia.edu-3",
                   "job-rivanna.hpc.virginia.edu-4",
                   "job-rivanna.hpc.virginia.edu-5", "end"]:
        Shell.copy(f"{shell_files_dir}/workflow-sh/{script}.sh", ".")
        assert os.path.isfile(f"./{script}.sh")

    w.add_job(name="start", kind=jobkind, user=user, host=host)
    w.add_job(name="end", kind=jobkind, user=user, host=host)

    for host, kind in [("localhost", jobkind),
                       ("rivanna", "ssh")]:

        # ("rivanna", "ssh")

        print("HOST:", host)
        user = login[host]["user"]
        host = login[host]["host"]
        # label = f'job-{host}-{n}'.replace('.hpc.virginia.edu', '')

        label = "'debug={cm.debug}\\nhome={os.HOME}\\n{name}\\n{now.%m/%d/%Y, %H:%M:%S}\\nprogress={progress}'"

        w.add_job(name=f"job-{host}-{n}", label=label,  kind=kind, user=user, host=host)
        n = n + 1
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
        n = n + 1
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
        n = n + 1

        first = n - 3
        second = n - 2
        third = n - 1
        w.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
        w.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
        w.add_dependencies(f"job-{host}-{third},end")
        w.add_dependencies(f"start,job-{host}-{first}")

    print(len(w.jobs) == n)
    g = str(w.graph)
    print(g)
    assert "name: start" in g
    assert "start-job-rivanna.hpc.virginia.edu-3:" in g
    return w

@pytest.mark.incremental
class TestService:

    def test_start_over(self):
        HEADING()
        create_dest()
        Benchmark.Start()
        #workflow_yaml = Shell.map_filename('./workflow-service.yaml').path
        workflow_dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-service/').path
        yaml_dir3 = Shell.map_filename('~/.cloudmesh/workflow/workflow-service/workflow-service.yaml').path
        Shell.rmdir(workflow_dir)
        assert not os.path.exists(workflow_dir)
        #create_dest()
        w = create_workflow(filename="workflow-service.yaml")

        print(w.filename)
        os.system("pwd")

        w.save_with_state('workflow-service.yaml')
        #w.save_with_state(filename=yaml_dir3)
        Benchmark.Stop()

    @pytest.mark.anyio
    async def test_home(self):
        HEADING()
        Benchmark.Start()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        Benchmark.Stop()

    def test_list_workflows(self):
        HEADING()
        Benchmark.Start()
        #  'headers': {'date': 'Fri, 05 Aug 2022 18:18:50 GMT', 'server': 'uvicorn', 'content-length': '65', 'content-type': 'application/json'},
        from cloudmesh.cc.workflowrest import RESTWorkflow
        rest = RESTWorkflow()
        result = rest.list_workflows()
        from pprint import pprint
        pprint(result.__dict__)
        assert result.status_code == 200
        # assert
        Benchmark.Stop()

    def test_upload_workflow(self):
        HEADING()
        Benchmark.Start()
        from cloudmesh.cc.workflowrest import RESTWorkflow
        rest = RESTWorkflow()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        expanded_dir_path = Shell.map_filename('./workflow-service/').path
        result = rest.upload_workflow(directory=f'{expanded_dir_path}/')
        from pprint import pprint
        print('here is pprint')
        pprint(result.__dict__)
        assert 'There was an error' not in result.text
        assert result.headers['content-type'] == 'application/json'
        assert result.status_code == 200
        assert type(result.json()) == dict

    def test_add_node(self):
        HEADING()
        Benchmark.Start()
        from cloudmesh.cc.workflowrest import RESTWorkflow
        rest = RESTWorkflow()
        result = rest.add_job(workflow_name='workflow-service', jobname='job01', user='jp', host='localhost', kind='local', script='c.sh', progress=4, status='ready')
        from pprint import pprint
        pprint(result.__dict__)
        assert result.headers['content-type'] == 'application/json'
        assert result.status_code == 200
        assert type(result.json()) == dict
        Benchmark.Stop()

    def test_get_workflow(self):
        HEADING()
        Benchmark.Start()
        from cloudmesh.cc.workflowrest import RESTWorkflow
        rest = RESTWorkflow()
        result = rest.get_workflow('workflow-service')
        from pprint import pprint
        pprint(result.__dict__)
        assert result.headers['content-type'] == 'application/json'
        assert result.status_code == 200
        assert type(result.json()) == dict
        result = rest.get_workflow(workflow_name='workflow-service', job_name='start')
        pprint(result.__dict__)
        assert result.headers['content-type'] == 'application/json'
        assert result.status_code == 200
        assert type(result.json()) == dict
        Benchmark.Stop()

    def test_run_workflow(self):
        HEADING()
        Benchmark.Start()
        from cloudmesh.cc.workflowrest import RESTWorkflow
        rest = RESTWorkflow()
        result = rest.run_workflow('workflow-service')
        from pprint import pprint
        pprint(result.__dict__)
        assert result.headers['content-type'] == 'text/html; charset=utf-8'
        assert result.status_code == 200
        #assert type(result.json()) == dict

class c:

    def test_delete_workflow(self):
        HEADING()
        Benchmark.Start()
        from cloudmesh.cc.workflowrest import RESTWorkflow
        rest = RESTWorkflow()
        result = rest.delete_workflow(workflow_name='workflow-service', job_name='start')
        from pprint import pprint
        pprint(result.__dict__)
        assert 'was deleted' in result.text
        assert result.headers['content-type'] == 'application/json'
        assert result.status_code == 200
        assert type(result.json()) == dict
        result = rest.delete_workflow(workflow_name='workflow-service')
        from pprint import pprint
        pprint(result.__dict__)
        assert 'was deleted' in result.text
        assert result.headers['content-type'] == 'application/json'
        assert result.status_code == 200
        assert type(result.json()) == dict

    def test_add_job(self):
        HEADING()
        Benchmark.Start()
        job = '{"name": "string","user": "string","host": "string","label": "string","kind": "string","status": "string","progress": 0,"script": "string","pid": 0,"parent": "string"}'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = client.post("/workflow/workflow-service",data=job,headers=headers)
        assert response.ok
        Benchmark.Stop()

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")