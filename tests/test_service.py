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
from cloudmesh.common.Shell import Shell
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.systeminfo import os_is_windows

banner(Path(__file__).name, c = "#", color="RED")

client = TestClient(app)

@pytest.mark.incremental
class TestService:

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
        list = glob.glob("~/.cloudmesh/workflow")
        print(list)
        # assert response.json() == {"workflows":list}
        Benchmark.Stop()

    def test_upload_workflow(self):
        HEADING()
        Benchmark.Start()
        files = {"file": open("./tests/workflow-source.yaml","rb")}
        response = client.post("/upload",files=files)
        Benchmark.Stop()
        assert response.status_code == 200

    # def test_add_job(self):
    #     HEADING()
    #     Benchmark.Start()
    #     job = '''{
    #       "name": "string",
    #       "user": "string",
    #       "host": "string",
    #       "label": "string",
    #       "kind": "string",
    #       "status": "string",
    #       "progress": 0,
    #       "script": "string",
    #       "pid": 0,
    #       "parent": "string"
    #     }'''
    #     headers = {
    #         'accept': 'application/json',
    #         'Content-Type': 'application/json'
    #     }
    #
    #     try:
    #         response = client.post("/workflow/workflow-source",data=job,headers=headers)
    #         Benchmark.Stop()
    #         assert response.ok
    #     except Exception as e:
    #         Benchmark.Stop()
    #         print("Exception:",e)

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
        response = client.get("/run?name=workflow&type=topo")
        Benchmark.Stop()
        assert response.status_code == 200

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")