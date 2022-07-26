###############################################################
# pytest -v --capture=no tests/test_service.py
# pytest -v  tests/test_service.py
# pytest -v --capture=no  tests/test_service.py::TestService::<METHODNAME>
###############################################################
import glob
from pathlib import Path

import os
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

def create_workflow():
    global w
    global username
    w = Workflow(filename=path_expand("tests/workflow-service.yaml"), clear=True)

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
        Benchmark.Start()
        yaml_dir = Shell.map_filename('~/cm/cloudmesh-cc/tests/workflow-service.yaml').path
        try:
            Shell.run(f'rm {yaml_dir}')
        except Exception as e:
            print(e)
        assert not os.path.exists(yaml_dir)
        destination = Shell.map_filename('~/.cloudmesh/workflow/workflow-source/').path
        destination2 = Shell.map_filename('~/.cloudmesh/workflow/workflow-service/').path
        print ("DDDD", destination)
        assert not os.path.exists(destination)
        assert not os.path.exists(destination2)
        w = create_workflow()
        w.save_with_state(yaml_dir)
        Benchmark.Stop()

    @pytest.mark.anyio
    async def test_home(self):
        HEADING()
        Benchmark.Start()
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        assert response.json() == {"msg": "cloudmesh.cc is up"}
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
        files = {"file": open("./tests/workflow-source.yaml","rb")}
        response = client.post("/upload",files=files)
        Benchmark.Stop()
        assert response.status_code == 200

    def test_add_job(self):
        HEADING()
        Benchmark.Start()
        job = '''{
          "name": "string",
          "user": "string",
          "host": "string",
          "label": "string",
          "kind": "string",
          "status": "string",
          "progress": 0,
          "script": "string",
          "pid": 0,
          "parent": "string"
        }'''
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = client.post("/workflow/workflow-source",json=job,headers=headers)
        Benchmark.Stop()
        assert response.ok


    def test_delete_workflow(self):
        HEADING()
        Benchmark.Start()
        response = client.delete("/workflow/workflow-source")
        Benchmark.Stop()
        assert response.status_code == 200

    def test_get_workflow(self):
        HEADING()
        Benchmark.Start()
        responsejob = client.get("/workflow/workflow?job=start")
        response = client.get("/workflow/workflow")
        Benchmark.Stop()
        assert response.status_code == 200
        assert responsejob.ok

    def test_run(self):
        HEADING()
        Benchmark.Start()
        # uploading the correct workflow
        files = {"file": open("./tests/workflow-service.yaml", "rb")}
        r = client.post("/upload", files=files)
        response = client.get("/run?name=workflow-service&type=topo")
        Benchmark.Stop()
        assert response.status_code == 200

    def test_benchmark(self):
        HEADING()
        response = client.delete("/workflow/workflow-service")
        Benchmark.print(csv=True, sysinfo=False, tag="cc")