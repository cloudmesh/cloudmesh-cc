###############################################################
# pytest -v --capture=no tests/test_service.py
# pytest -v  tests/test_service.py
# pytest -v --capture=no  tests/test_service.py::TestService::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from fastapi.testclient import TestClient

import cloudmesh.cc.service
from cloudmesh.cc.service.service import app


client = TestClient(app)

@pytest.mark.incremental
class TestService:

    def test_home(self):
        HEADING()
        Benchmark.Start()
        response = client.get("/")
        Benchmark.Stop()
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello World"}


    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")
