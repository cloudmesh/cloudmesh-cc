# ##############################################################
# pytest -v -x --capture=no tests/test_080_workflow_clean.py
# pytest -v  tests/test_080_workflow_clean.py
# pytest -v --capture=no  tests/test_080_workflow_clean.py::TestWorkflowLocal::<METHODNAME>
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
from cloudmesh.common.DateTime import DateTime
# from utilities import set_host_user

"""
This is a python file to test the implementation of workflow in running a
clean, self-contained workflow.
"""

#location = Shell.map_filename("./tests/mnist").path
#os.chdir(location)

username = Shell.sys_user()
utilities.create_dest()

def create_workflow(filename='workflow-clean.yaml'):
    global w
    global username
    w = Workflow(filename=filename, load=False)

    localuser = Shell.sys_user()
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"}
    }

    n = 0

    user = login["localhost"]["user"]
    host = login["localhost"]["host"]

    jobkind = "local"

    for script in ["start.sh", "b.sh", "c.py", "d.ipynb", "end.sh"]:
        Shell.copy(f"../workflow-clean/{script}", ".")
        assert os.path.isfile(f"./{script}")

    w.add_job(name="start", kind=jobkind, user=user, host=host)
    w.add_job(name="end", kind=jobkind, user=user, host=host)


    t0 = DateTime.now()
    for host, kind in [("localhost", jobkind)]:

        print("HOST:", host)
        user = login[host]["user"]
        host = login[host]["host"]
        # label = f'job-{host}-{n}'.replace('.hpc.virginia.edu', '')

        #label = "{name}\\n{now.%m/%d/%Y, %H:%M:%S}\\n{modified.%m/%d/%Y, %H:%M:%S}\\n{created.%m/%d/%Y, %H:%M:%S}\\nprogress={progress}"
        label = "{name}\\n{now.%m/%d/%Y, %H:%M:%S}\\nprogress={progress}"

        w.add_job(name=f"b.sh", label=label,  kind=kind, user=user, host=host)
        w.add_job(name=f"c.py", label=label, kind=kind, user=user, host=host)
        w.add_job(name=f"d.ipynb", label=label, kind=kind, user=user, host=host)

        w.add_dependencies(f"b.sh,c.py")
        w.add_dependencies(f"c.py,d.ipynb")
        w.add_dependencies(f"d.ipynb,end")
        w.add_dependencies(f"start,b.sh")

    # print(len(w.jobs) == n)
    g = str(w.graph)
    print(g)
    assert "name: start" in g
    assert "start-b.sh:" in g
    return w

@pytest.mark.incremental
class TestCleanWorkflow:

    def test_reset_experiment_dir(self):
        os.system("rm -rf ~/experiment")
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)

        assert not os.path.exists(exp)

    def test_create_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = create_workflow()
        Benchmark.Stop()
        g = str(w.graph)
        print(g)
        assert "start" in g
        assert "host: local" in g
        print(w.graph)

    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="workflow-clean.svg", colors="status",  engine="dot")
        Shell.open("workflow-clean.svg")
        # assert os.path.exists("~/tmp/test-dot.svg") == True

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        s1 = w["start"]
        s2 = w.job("start")
        Benchmark.Stop()
        print(s1)
        assert s1 == s2

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        print(w.table)
        print(w.table2(with_label=True))
        Benchmark.Stop()
        assert True

    def test_order(self):
        HEADING()
        global w
        Benchmark.Start()
        order = w.sequential_order()
        Benchmark.Stop()
        print(order)
        assert len(order) == len(w.jobs)

    def test_run_topo(self):
        HEADING()
        Benchmark.Start()
        w.run_topo(show=True, filename="topo-clean.svg")
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)
