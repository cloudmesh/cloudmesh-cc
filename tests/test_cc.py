###############################################################
# pytest -v --capture=no tests/test_cc.py
# pytest -v  tests/test_cc.py
# pytest -v --capture=no  tests/test_cc.py::Test_cc::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class TestConfig:

    def test_help(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms cc help", shell=True)
        Benchmark.Stop()
        VERBOSE(result)

        assert "cc add --queue=QUEUE --job=JOB --command=COMMAND" in result
        assert "upload" in result
        assert "start" in result

class rest:

    def test_queue_create(self):
        HEADING()
        Benchmark.Start()
        result = Shell.execute("cms cc create localhost", shell=True)
        Benchmark.Stop()
        VERBOSE(result)
        assert "quit" in result
        assert "clear" in result

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")
