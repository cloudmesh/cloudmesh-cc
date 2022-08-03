###############################################################
# pytest -v -x --capture=no tests/test_032_job_localhost_filetype.py
# pytest -v  tests/test_032_job_localhost_filetype.py
# pytest -v --capture=no  tests/test_032_job_localhost_filetype.py::TestJobLocalhost::<METHODNAME>
###############################################################

#
# program needs pip install pywin32 -U in requirements if on the OS is Windows
# TODO: check if pywin32 is the correct version
#

import os
import shutil
import subprocess
from pathlib import Path

import pytest
import time

from cloudmesh.cc.job.localhost.Job import Job
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
from cloudmesh.common.variables import Variables
from cloudmesh.cc.workflow import Workflow

banner(Path(__file__).name, c = "#", color="RED")

Shell.rmdir("dest")
Shell.mkdir("dest")
os.chdir("dest")

@pytest.mark.incremental
class TestJobLocalhost:

    def test_sh(self):
        HEADING()
        from cloudmesh.cc.job.localhost.Job import Job
        job = Job(name="hallo")
        print(job)

        script = job.create(filename="a.sh",
                            script="b.sh")

        exec = job.create(filename="c.sh",
                          exec="b.sh")
        # print (script)

        banner("a.sh sh")
        a = Shell.cat("a.sh")
        print(a)
        banner("b.sh sh")

        c = Shell.cat("c.sh")
        print(c)

        assert a == script
        assert a == c

    def test_py(self):
        HEADING()
        from cloudmesh.cc.job.localhost.Job import Job
        job = Job(name="hallo")
        print (job)

        script = job.create(filename="a.sh",
                            script="python a.py")
        exec = job.create(filename="b.sh",
                          exec="a.py")

        #print (script)


        banner("a.sh python")
        a = Shell.cat("a.sh")
        print(a)
        banner("b.sh python")

        b = Shell.cat("b.sh")
        print(b)

        assert a == script
        assert a == b

    def test_ipynb(self):
        HEADING()
        from cloudmesh.cc.job.localhost.Job import Job
        job = Job(name="hallo")
        print(job)

        script = job.create(filename="a.sh",
                            script="papermill a.ipynb a-output.ipynb")

        exec = job.create(filename="b.sh",
                            exec="a.ipynb")

        # print (script)


        banner("a.sh notebook")
        a = Shell.cat("a.sh")
        print(a)
        banner("b.sh notebook")

        b = Shell.cat("b.sh")
        print(b)

        assert a == script
        assert a == b

    def test_mnist(self):
        HEADING()

        w = Workflow()
        location = path_expand("../tests/mnist/source-mnist-exec.yaml")

        r = Shell.cat(location)
        w.load(filename=location, clear=True)

        w.display()

        w.run_topo()

        w.display()
