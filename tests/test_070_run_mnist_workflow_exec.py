# ##############################################################
# pytest -v -x --capture=no tests/test_070_run_mnist_workflow_exec.py
# pytest -v  tests/test_070_run_mnist_workflow_exec.py
# pytest -v --capture=no  tests/test_070_run_mnist_workflow_exec.py::TestWorkflowLocal::<METHODNAME>
# ##############################################################
import os.path
import shutil
from pathlib import Path
import pytest

import networkx as nx

from cloudmesh.cc.workflow import Workflow
import utilities
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
from cloudmesh.common.variables import Variables
from pprint import pprint
# from utilities import set_host_user

"""
This is a python file to test the implementation of workflow in running the 
mnist files. 
"""

#location = Shell.map_filename("./tests/mnist").path
#os.chdir(location)
utilities.create_dest()


@pytest.mark.incremental
class TestMnist:

    def test_mnist(self):
        HEADING()
        utilities.create_dest()
        if os.path.isdir('./mnist'):
            Shell.rmdir('./mnist')
        Shell.mkdir('./mnist')
        os.chdir('./mnist')
        Shell.mkdir('./runtime')
        os.chdir('./runtime')

        # copy shell files
        shell_files = Path(f'{__file__}').as_posix()

        for script in ["start", "prepare", "mlp_mnist", "example_mlp_mnist",
                       "end"]:
            Shell.copy(f"{shell_files}/../mnist/{script}.sh", ".")
            assert os.path.isfile(f"./{script}.sh")
        os.chdir('..')
        Shell.copy_file(f"{shell_files}/../mnist/source-mnist.yaml",
                        "./mnist.yaml")
        filename = Shell.map_filename("./mnist.yaml").path
        r = Shell.ls()
        pprint(r)

        w = Workflow()
        w.load(filename=filename)
        print(w)
        w.save(filename=filename)
        #w.load(filename=filename)
        w.display(name='mnist')
        w.run_topo(show=True)
        utilities.create_dest()
        Shell.rmdir('./mnist')