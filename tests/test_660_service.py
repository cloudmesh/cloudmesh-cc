###############################################################
# pytest -v --capture=no tests/test_660_service.py
# pytest -v  tests/test_660_service.py
# pytest -v --capture=no  tests/test_660_service.py::TestService::<METHODNAME>
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

create_workflow_service()

banner(Path(__file__).name, c="#", color="RED")


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
    w = Workflow(name="workflow-service", load=False)

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
    shell_files_dir = Path(os.path.dirname(shell_files)).as_posix()
    runtime_dir = Path(Shell.map_filename(
        '~/.cloudmesh/workflow/workflow-service/runtime').path).as_posix()
    #os.chdir('workflow-service')
    #Shell.mkdir('runtime')
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

        label = "'debug={cm.debug}\\nhome={os.HOME}\\n{name}\\n{now.%m/%d/%Y, %H--%M--%S}\\nprogress={progress}'"

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
        Benchmark.Start()
        #workflow_yaml = Shell.map_filename('./workflow-service.yaml').path
        workflow_dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-service/').path
        yaml_dir3 = Shell.map_filename('~/.cloudmesh/workflow/workflow-service/workflow-service.yaml').path
        try:
            Shell.run(f'rm -rf {workflow_dir}')
        except Exception as e:
            print(e)
        assert not os.path.exists(workflow_dir)
        w = create_workflow(filename="workflow-service.yaml")

        w.save_with_state('workflow-service.yaml')
        os.system('ls')
        os.system('pwd')
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
        response = client.get("/workflows")
        assert response.status_code == 200
        print(Shell.run("ls ~/.cloudmesh/workflow"))
        # assert response.json() == {"workflows":list}
        Benchmark.Stop()

    def test_upload_workflow(self):
        HEADING()
        Benchmark.Start()
        # files = {"file": open("./workflow-service.yaml","rb")}
        create_workflow()
        os.chdir('..')
        workflow_service_dir = path_expand(__file__)


        workflow_service_dir = os.path.dirname(workflow_service_dir)
        os.chdir(workflow_service_dir)
        os.chdir('./workflow-service')
        workflow_service_dir = os.getcwd()
        #workflow_service_dir = Path(workflow_service_dir).as_posix()
        workflow_service_dir = '~/cm/cloudmesh-cc/tests/workflow-service'

        response = client.post(f"/workflow/upload?directory={workflow_service_dir}")
        Benchmark.Stop()
        assert response.status_code == 200

    def test_get_workflow(self):
        HEADING()
        Benchmark.Start()
        responsejob = client.get("/workflow/workflow-service/job/start")
        response = client.get("/workflow/workflow-service")
        Benchmark.Stop()
        assert response.status_code == 200
        assert responsejob.ok

    def test_run(self):
        HEADING()
        Benchmark.Start()
        response = client.get("/workflow/run/workflow-service")
        Benchmark.Stop()
        assert response.status_code == 200

    # this should be fixed since it overwrites the yaml thats supposed to stay
    # original. in ~/.cloudmesh/workflow/workflow-service/workflow-service.yaml
    # it changes thanks to this function test_add_job
    def test_add_job(self):
        HEADING()
        Benchmark.Start()
        #job = '{"name": "string","user": "string","host": "string","label": "string","kind": "string","status": "string","progress": 0,"script": "string","pid": 0,"parent": "string"}'
        job = "string"
        user = "string"
        host = "string"
        label = "string"
        kind = "string"
        status = "string"
        progress = 2
        script = "string"

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = client.post(f"/workflow/workflow-service/job/{job}?user={user}&host={host}&label={label}&kind={kind}&status={status}&progress={progress}&script={script}")
        print(response)
        print(response.text)
        assert response.ok
        Benchmark.Stop()

    def test_delete_workflow(self):
        HEADING()
        Benchmark.Start()
        response = client.delete("/workflow/workflow-service")
        Benchmark.Stop()
        assert response.status_code == 200

    def test_benchmark(self):
        os.chdir(os.path.dirname(__file__))
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")