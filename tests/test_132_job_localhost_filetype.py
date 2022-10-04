###############################################################
# pytest -v -x --capture=no tests/test_032_job_localhost_filetype.py
# pytest -v  tests/test_032_job_localhost_filetype.py
# pytest -v --capture=no  tests/test_032_job_localhost_filetype.py::TestJobLocalhost::<METHODNAME>
###############################################################

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
from utilities import create_dest

create_dest()

banner(Path(__file__).name, c="#", color="RED")


@pytest.mark.incremental
class TestJobLocalhost:

    def test_sh(self):
        HEADING()
        create_dest()
        from cloudmesh.cc.job.localhost.Job import Job
        Shell.mkdir('job-localhost-filetype')
        os.chdir('job-localhost-filetype')
        Shell.mkdir('runtime')
        os.chdir('runtime')
        job = Job(name="hallo")
        print(job)

        script = job.create(filename="a.sh",
                            script="b.sh")

        exec = job.create(filename="c.sh",
                          exec="b.sh")
        # print(script)

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
        print(job)

        script = job.create(filename="a.sh",
                            script="python a.py")
        exec = job.create(filename="b.sh",
                          exec="a.py")

        #print(script)


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

        w = Workflow(name='mnist')
        os.chdir(os.path.dirname(__file__))
        location = path_expand("./mnist/source-mnist-exec.yaml")

        r = Shell.cat(location)
        w.load(filename=location)
        create_dest()

        Shell.mkdir('mnist')
        os.chdir('mnist')
        Shell.mkdir('./runtime')
        os.chdir('./runtime')

        shell_files = Path(f'{__file__}').as_posix()
        shell_files_dir = Path(os.path.dirname(shell_files)).as_posix()
        for script in ["start", "example_mlp_mnist", "end"]:
            Shell.copy(f"{shell_files_dir}/mnist/{script}.sh", ".")
        os.chdir('..')

        w.display()

        w.run_topo()

        w.display()
        print(w.table)
        create_dest()
        Shell.rmdir('./job-localhost-filetype')
        # time.sleep(10)
