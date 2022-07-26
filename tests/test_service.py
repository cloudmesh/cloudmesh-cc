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
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.util import readfile
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.systeminfo import os_is_windows

banner(Path(__file__).name, c = "#", color="RED")

client = TestClient(app)

@pytest.mark.incremental
class TestService:

    def test_start_over(self):
        HEADING()
        Benchmark.Start()
        os.system('rm -f ~/.cloudmesh/workflow/workflow-source/workflow-source.yaml')
        # os.system('mkdir -p  ~/.cloudmesh/workflow/workflow-source/')
        dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-source/workflow-source.yaml').path
        Shell.copy_file(f"https://raw.githubusercontent.com/cloudmesh/cloudmesh-cc/main/tests/workflow-source.yaml",
                    f"{dir}/workflow-source.yaml")
        assert os.path.exists(Shell.map_filename("~/.cloudmesh/workflow/workflow-source/workflow-source.yaml").path)
        Benchmark.Stop()

class a:

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
        dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-source/workflow-source.yaml').path
        files = {"file": open(dir, "rb")}
        response = client.post("/upload",files=files)
        Benchmark.Stop()
        assert response.status_code == 200

    def test_add_job(self):
        HEADING()
        # w = Workflow(filename='workflow.yaml', name='workflow')
        #global w
        #w = Workflow(filename="tests/workflow-source.yaml")
        # w.save('~/.cloudmesh/workflow/workflow/workflow.yaml')
        Benchmark.Start()
        job = {
          "name": "job1",
          "user": "gregor",
          "host": "localhost",
          "label": "simple",
          "kind": "localhost",
          "status": "undefined",
          "script": "nothing.sh"
        }
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        try:
            response = client.post("/job_add/workflow-source", json=job, headers=headers)
            Benchmark.Stop()
            assert response.ok
        except Exception as e:
            Benchmark.Stop()
            print("Exception:",e)

    def test_get_workflow(self):
        HEADING()
        Benchmark.Start()
        responsejob = client.get("/workflow/workflow-source?job=start")
        response = client.get("/workflow/workflow-source")
        Benchmark.Stop()
        assert response.status_code == 200
        assert responsejob.ok

    def test_run(self):
        HEADING()
        Benchmark.Start()
        dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-source/workflow-source.yaml').path
        # uploading the correct workflow
        files = {"file": open(dir, "rb")}
        r = client.post("/upload", files=files)
        response = client.get("/run/workflow-source?type=topo")
        Benchmark.Stop()
        assert response.status_code == 200

class b:

    def test_delete_workflow(self):
        HEADING()
        Benchmark.Start()
        response = client.delete("/workflow/workflow-source")
        Benchmark.Stop()
        assert response.status_code == 200

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")