# ##############################################################
# pytest -v -x --capture=no tests/test_workflow_local.py
# pytest -v  tests/test_workflow.py
# pytest -v --capture=no  tests/workflow.py::TestWorkflowLocal::<METHODNAME>
# ##############################################################
import os.path
import shutil
from pathlib import Path

import networkx as nx

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell
from cloudmesh.common.variables import Variables

# from utilities import set_host_user

"""
    This is a python file to test to make sure the workflow class works.
    It will draw upon the the test_queues file, because there is a file that
    was created with a bunch of jobs. 
"""

banner(Path(__file__).name, c = "#", color="RED")

variables = Variables()

name = "run"

# host, username = set_host_user()

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

if "username" in variables:
    username = variables["username"]
else:
    username = os.path.basename(os.environ["HOME"])

global w


def create_workflow():
    global w
    global username
    w = Workflow(filename=path_expand("tests/workflow.yaml"), clear=True)

    if os_is_windows():
        localuser = os.environ["USERNAME"]
    else:
        try:
            localuser = os.environ['USER']
        except:
            # docker image does not have user variable. so just do basename of home
            localuser = os.system('basename $HOME')
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"},
        "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
        "pi": {"user": f"{localuser}", "host": "red"},
    }

    n = 0

    user = login["localhost"]["user"]
    host = login["localhost"]["host"]

    jobkind="local"

    w.add_job(name="start", kind=jobkind, user=user, host=host)
    w.add_job(name="end", kind=jobkind, user=user, host=host)

    # w.add_job(name="start", kind="local", user=user, host=host)
    # w.add_job(name="end", kind="local", user=user, host=host)

    # for host, kind in [("localhost", "local"),
    #                    ("rivanna", "local")]:
    for host, kind in [("localhost", jobkind),
                       ("rivanna", jobkind)]:

        # ("rivanna", "ssh")

        print("HOST:", host)
        user = login[host]["user"]
        host = login[host]["host"]
        # label = f'job-{host}-{n}'.replace('.hpc.virginia.edu', '')

        label = "'debug={cm.debug}\\nhome={os.HOME}\\n{name}\\n{now.%m/%d/%Y, %H:%M:%S}\\nprogress={progress}'"

        w.add_job(name=f"job-{host}-{n}", label=label,  kind=kind, user=user, host=host)
        n = n + 1
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
        n = n + 1
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
        n = n + 1

        first = n - 3
        second = n - 2
        third = n - 1
        w.add_dependencies(f"job-{host}-{first},job-{host}-{second}")
        w.add_dependencies(f"job-{host}-{second},job-{host}-{third}")
        w.add_dependencies(f"job-{host}-{third},end")
        w.add_dependencies(f"start,job-{host}-{first}")

    print(len(w.jobs) == n)
    g = str(w.graph)
    print(g)
    assert "name: start" in g
    assert "start-job-rivanna.hpc.virginia.edu-3:" in g
    return w


class TestWorkflowLocal:

    def test_experiment_setup(self):
        full_dir = Shell.map_filename('~/experiment').path
        try:
            r = Shell.run(f"rm -rf {full_dir}")
            r = Shell.run(f'ssh {username}@{host} "rm -rf ~/experiment"')
        except Exception as e:
            print(e.output)
        # copy all files needed into experiment
        # run all other tests in ./experiment_ssh
        # os.chdir("./experiment_ssh")
        # then run all test there

    def test_load_workflow(self):
        HEADING()
        global w
        Benchmark.Start()
        w = Workflow()
        w.load(filename=path_expand('tests/workflow.yaml'), clear=True)
        Benchmark.Stop()
        g = str(w.graph)
        print(g)
        assert w.filename == path_expand("~/.cloudmesh/workflow/workflow.yaml")
        assert "start" in g
        assert "host: local" in g

    def test_reset_experiment_dir(self):
        os.system("rm -rf ~/experiment")
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)
        os.system('cp tests/workflow-sh/*.sh .')
        assert not os.path.isfile(exp)

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        Benchmark.Start()
        w = create_workflow()
        Benchmark.Stop()
        g = str(w.graph)
        print(g)
        assert "name: start" in g
        assert "start-job-rivanna.hpc.virginia.edu-3:" in g

    def test_show(self):
        HEADING()
        global w
        if os_is_windows():
            try:
                w.graph.save(filename="test-dot.svg", colors="status", engine="dot")
            except Exception as e:
                print(e)
        else:
            w.graph.save(filename="/tmp/test-dot.svg", colors="status", engine="dot")
        # Shell.browser("/tmp/test-dot.svg")
        if os_is_windows():
            os.path.exists("test-dot.svg")
        else:
            os.path.exists("/tmp/test-dot.svg")

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        job_start_1 = w["start"]
        job_start_2 = w.job("start")
        Benchmark.Stop()
        print(job_start_1)
        assert job_start_1 == job_start_2
        assert job_start_1["name"] == "start"

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        print(w.table)
        Benchmark.Stop()
        t = str(w.table)
        assert "| progress |" in t
        assert "job-rivanna.hpc.virginia.edu-3" in t
        assert "job-rivanna.hpc.virginia.edu-3" in t

    def test_order(self):
        HEADING()
        global w
        Benchmark.Start()
        order = w.sequential_order()
        Benchmark.Stop()
        print(order)
        assert len(order) == len(w.jobs)
        for i in range(1, len(order)):
            parent = order[i - 1]
            name = order[i]
            assert name not in w[parent]['parent']

    def test_run_topo(self):
        HEADING()
        w = create_workflow()
        Benchmark.Start()
        w.run_topo(show=True, filename="topo.svg")
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)

        for name, node in w.jobs.items():
            assert node["progress"] == 100
            assert node["parent"] == []
            assert node["status"] == "done"

    # def test_run_parallel(self):
    #     HEADING()
    #     w = create_workflow()
    #     Benchmark.Start()
    #     w.run_parallel(show=True, period=1.0, filename="parallel.svg")
    #     Benchmark.Stop()
    #     banner("Workflow")
    #     print(w.graph)
    #     for name, node in w.jobs.items():
    #         assert node["progress"] == 100
    #         assert node["parent"] == []
    #         assert node["status"] == "done"

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
