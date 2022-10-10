###############################################################
# pytest -v --capture=no tests/test_012_service_localhost.py
# pytest -v  tests/test_012_service_localhost.py
# pytest -v --capture=no  tests/test_012_service_localhost.py::TestService::<METHODNAME>
###############################################################
import requests
import pytest
from fastapi.testclient import TestClient
from cloudmesh.cc.service.service import app
from cloudmesh.common.util import HEADING
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.cc.service.service import get_available_workflows
from httpx import AsyncClient

client = TestClient(app)

@pytest.mark.incremental
class TestService:

    @pytest.mark.anyio
    async def test_home(self):
        HEADING()
        Benchmark.Start()
        async with AsyncClient(app=app, base_url="http://127.0.0.1") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        Benchmark.Stop()

    def test_list_workflows(self):
        HEADING()

        Benchmark.Start()
        response = client.get("/workflows")
        print(response.json())
        # result = Shell.run("ls ~/.cloudmesh/workflow").splitlines()
        result = get_available_workflows()
        print(result)
        assert len(response.json()['workflows']) == len(result)
        assert response.status_code == 200
        # assert response.json() == {"workflows":list}
        Benchmark.Stop()
