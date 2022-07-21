###############################################################
# pytest -v --capture=no tests/test_service.py
# pytest -v  tests/test_service.py
# pytest -v --capture=no  tests/test_service.py::TestService::<METHODNAME>
###############################################################
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cloudmesh.cc.service.service import app
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner

banner(Path(__file__).name, c = "#", color="RED")

client = TestClient(app)


@pytest.mark.incremental
class TestService:

    def test_home(self):
        HEADING()
        Benchmark.Start()
        response = client.get("/")
        Benchmark.Stop()
        assert response.status_code == 200
        assert response.json() == {"msg": "cloudmesh.cc is up"}

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")

    def test_post_queue(self):
        HEADING()
        Benchmark.Start()
        app.post("/post/job")
        Benchmark.Stop()


