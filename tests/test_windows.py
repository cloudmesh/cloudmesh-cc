###############################################################
# pytest -v --capture=no tests/test_windows.py
# pytest -v  tests/test_windows.py
# pytest -v --capture=no  tests/test_windows.py::Test_cc::<METHODNAME>
###############################################################
import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class TestConfig:

    def test_Shell_run(self):
        HEADING()
        Benchmark.Start()
        result = Shell.run("cms cc help")
        Benchmark.Stop()
        VERBOSE(result)

        assert "cc add --queue=QUEUE --job=JOB --command=COMMAND" in result
        assert "upload" in result
        assert "start" in result

    def test_Shell_mkdir(self):
        HEADING()
        Benchmark.Start()
        result = Shell.mkdir("~/a_dir")
        Benchmark.Stop()
        VERBOSE(result)



class rest:
    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")
