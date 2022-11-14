###############################################################
# pytest -v --capture=no tests/test_002_cc_labelmaker.py
# pytest -v  tests/test_002_cc_labelmaker.py
# pytest -v --capture=no  tests/test_002_cc_labelmaker.py::test__002_cc_labelmaker::<METHODNAME>
###############################################################

from pathlib import Path

import pytest

from cloudmesh.cc.labelmaker import Labelmaker
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
import os
from utilities import create_dest

create_dest()

banner(Path(__file__).name, c="#", color="RED")

@pytest.mark.incremental
class TestLabelmaker:

    def test_label(self):
        HEADING()

        Benchmark.Start()

        label = Labelmaker("name={name} home={os.HOME} debug={cm.debug} date={now.%m/%d/%Y, %H--%M--%S}",
                           'sample-workflow',
                           'sample-job')

        d = {"name": "gregor"}
        r = label.get(**d)

        Benchmark.Stop()


        print(r)
        assert r.startswith(f"name=gregor home={str(Shell.map_filename('~').path).encode('unicode-escape').decode()}")

    def test_benchmark(self):
        HEADING()
        Benchmark.print(csv=True, sysinfo=False, tag="cc")
