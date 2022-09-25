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

name = "run"
variables = Variables()

host = "rivanna.hpc.virginia.edu"
username = variables["username"]

def create_workflow(filename='mnist.yaml'):
    global w
    global username
    w = Workflow(filename=filename, load=False)

    localuser = Shell.sys_user()
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"},
        "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"}
    }

    utilities.create_dest()
    if os.path.isdir('./mnist'):
        Shell.rmdir('./mnist')
    Shell.mkdir('./mnist')
    os.chdir('./mnist')
    Shell.mkdir('./runtime')
    os.chdir('./runtime')

    # copy shell files
    shell_files = Path(f'{__file__}').as_posix()
    shell_files_dir = Path(os.path.dirname(shell_files)).as_posix()

    for script in ["prepare", "end"]:
        Shell.copy(f"{shell_files_dir}/mnist/{script}.sh", ".")
        assert os.path.isfile(f"./{script}.sh")

    for script in ["run_all_rivanna"]:
        Shell.copy(f"{shell_files_dir}/mnist/{script}.py", ".")
        assert os.path.isfile(f"./{script}.py")
    os.chdir('..')

    label = "{name}\\nprogress={progress}"

    w.add_job(name=f"prepare", label=label,  kind='ssh', user=username,
              host=host)
    w.add_job(name=f"run_all_rivanna.py", label=label, kind='ssh', user=username,
              host=host, script="run_all_rivanna.py")
    w.add_job(name=f"end", label=label, kind='ssh', user=username, host=host)

    w.add_dependencies(f"prepare,run_all_rivanna")
    w.add_dependencies(f"run_all_rivanna,end")
    w.graph.save_to_yaml("./mnist.yaml")
    Shell.copy("./mnist.yaml", "./runtime/mnist.yaml")
    g = str(w.graph)
    print(g)
    return w

@pytest.mark.incremental
class TestMnist:

    def test_mnist(self):
        HEADING()

        w = create_workflow()
        print(w)
        #w.load(filename=filename)
        w.display(name='mnist')
        w.run_topo(show=True)
        utilities.create_dest()
        Shell.rmdir('./mnist')