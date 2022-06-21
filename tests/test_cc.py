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
        result = Shell.run("cms cc help")
        Benchmark.Stop()
        VERBOSE(result)

        assert "cc add --queue=QUEUE --job=JOB --command=COMMAND" in result
        assert "upload" in result
        assert "start" in result


    def test_queue_create(self):
        HEADING()
        QUEUES = 'testqueue'
        DATABASE= 'yamldb'
        Benchmark.Start()
        result = Shell.run(f"cms cc create --queues={QUEUES} "
                               f"--database={DATABASE}")
        Benchmark.Stop()
        VERBOSE(result)
        assert '' in result
        result = Shell.run(f'cms cc list --queue={QUEUES}')
        print(result)

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")
