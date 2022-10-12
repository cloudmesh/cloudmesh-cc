# ##############################################################
# pytest -v -x --capture=no tests/test_131_workflow_local.py
# pytest -v  tests/test_131_workflow_local.py
# pytest -v --capture=no  tests/test_131_workflow_local.py::TestWorkflowLocal::<METHODNAME>
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
from utilities import create_dest, set_host_user

create_dest()

# from utilities import set_host_user

banner(Path(__file__).name, c="#", color="RED")


variables = Variables()


name = "run"

host, username = set_host_user()

w = None


def create_workflow(filename='./workflow-local.yaml'):
    global w
    global username
    w = Workflow(name='workflow-local', load=False)

    localuser = Shell.sys_user()
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"},
        "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
        "pi": {"user": f"{localuser}", "host": "red"},
    }

    n = 0

    user = login["localhost"]["user"]
    host = login["localhost"]["host"]

    jobkind = "local"

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

        label = "debug={cm.debug}\\nhome={os.HOME}\\n{name}\\n{now.%m/%d/%Y, %H--%M--%S}\\nprogress={progress}"
        label_format = label
        w.add_job(name=f"job-{host}-{n}", label=label, kind=kind, user=user, host=host)
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
    w.save(filename=filename)
    assert "name: start" in g
    assert "start-job-rivanna.hpc.virginia.edu-3:" in g
    return w

def remove_workflow():
    create_dest()
    workflow_local_dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-local').path

    # Remove experiment execution directory
    full_dir = Shell.map_filename('~/experiment').path

    Shell.rmdir(full_dir)

    # remove locat workflow file, for state notification
    Shell.rmdir(workflow_local_dir)

    # logic
    # 1. copy testsdef remove_workflow(filename="tests/workflow.yaml"):
    #     # Remove workflow source yaml filr
    #     Shell.rm(filename)
    #
    #     # Remove experiment execution directory
    #     full_dir = Shell.map_filename('~/experiment').path
    #
    #     # TODO:
    #     # r = Shell.rmdir(full_dir)
    #     r = Shell.run(f"rm -fr {full_dir}")
    #
    #     # remove locat workflow file, for state notification
    #     Shell.rm("~/.cloudmesh/workflow")
    #
    #     # logic
    #     # 1. copy tests/workflow.yaml to local dir simulation from where we start the workflow
    #     # 2. copy the workflow to ~/experiment wher it is executed
    #     # 3. copy the workflow log file to ~/.cloudmesh/workflow/workflow wher the directory is that
    #     #     we observeve that changes
    #     # Why do we need the ~/.cloudmesh dir
    #     # * it simulates a remote computer as it would be have ther, as the execution is done
    #     #   on the remote computer in a ~/experiment dir. There may be a benefit to have the same
    #     #   experiment dir locally, but this can not be done for localhost, so we use .cloudmesh
    #     # * for ssh slurm and others we simply use ~/experiment
    #     # maybe we just simplify and do not copy and keep it in .cloudmesh ... or experiment
    #
    #     for filename in [
    #             'tests/workflow.yaml',
    #             '~/experiment',
    #             "~/.cloudmesh/workflow/workflow",
    #             "~/.cloudmesh/workflow/workflow/workflow.yaml"
    #         ]:
    #             where = Shell.map_filename(filename).path
    #             assert not os.path.exists(where)tests//workflow.yaml to local dir simulation from where we start the workflow
    # 2. copy the workflow to ~/experiment wher it is executed
    # 3. copy the workflow log file to ~/.cloudmesh/workflow/workflow wher the directory is that
    #     we observeve that changes
    # Why do we need the ~/.cloudmesh dir
    # * it simulates a remote computer as it would be have ther, as the execution is done
    #   on the remote computer in a ~/experiment dir. There may be a benefit to have the same
    #   experiment dir locally, but this can not be done for localhost, so we use .cloudmesh
    # * for ssh slurm and others we simply use ~/experiment
    # maybe we just simplify and do not copy and keep it in .cloudmesh ... or experiment

    for filename in [
            '~/experiment',
            "~/.cloudmesh/workflow/workflow-local",
            "~/.cloudmesh/workflow/workflow-local/workflow-local.yaml"
        ]:
            where = Shell.map_filename(filename).path
            assert not os.path.exists(where)


banner("TEST START")


class TestWorkflowLocal:
    def test_single_test(self):
        HEADING()
        global w

        remove_workflow()

        #reset
        Shell.rmdir('./workflow-local')

        Shell.mkdir('./workflow-local')
        os.chdir('./workflow-local')

        # write a yaml file
        w = create_workflow()

        # copy shell files
        shell_files = Path(f'{__file__}').as_posix()
        shell_files_dir = Path(os.path.dirname(shell_files)).as_posix()
        runtime_dir = Path(Shell.map_filename(
            '~/.cloudmesh/workflow/workflow-local/runtime').path).as_posix()
        try:
            Shell.run(f'cp {shell_files_dir}/workflow-sh/*.sh {runtime_dir}')
        except Exception as e:
            print(e.output)

        g = str(w.graph)
        print(g)

        assert w.filename == path_expand("~/.cloudmesh/workflow/workflow-local/workflow-local.yaml")
        assert "start" in g
        assert "host: local" in g

    def test_show(self):
        HEADING()
        global w
        w.graph.save(filename="test-dot.svg", colors="status", engine="dot")
        # Shell.browser("test-dot.svg")
        os.path.exists("test-dot.svg")

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
        global w
        Benchmark.Start()
        w.run_topo(show=True)
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)

        for name, node in w.jobs.items():
            assert node["progress"] == 100
            assert node["parent"] == []
            assert node["status"] == "done"

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")


class b:
    def test_load_workflow(self):
        HEADING()
        global w


        Benchmark.Start()
        remove_workflow(filename="workflow-local.yaml")

        w0 = create_workflow()
        w0.save('workflow-local.yaml')

        w = Workflow(name='workflow-local')
        w.load(filename='workflow-local.yaml')

        Benchmark.Stop()
        g = str(w.graph)
        print(g)

        assert w.filename == path_expand("~/.cloudmesh/workflow/workflow-local/workflow-local.yaml")
        assert "start" in g
        assert "host: local" in g

    def test_reset_experiment_dir(self):
        HEADING()
        os.system("rm -rf ~/experiment")
        exp = path_expand("~/experiment")
        shutil.rmtree(exp, ignore_errors=True)
        shell_files = Path(f'{__file__}').as_posix()
        runtime_dir = Path(Shell.map_filename('~/.cloudmesh/workflow/workflow-local/runtime').path).as_posix()
        os.system(f'cp {shell_files}/../workflow-sh/*.sh {runtime_dir}')
        assert not os.path.isfile(exp)

        banner("pwd")
        os.system("pwd")

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w

        Benchmark.Start()
        remove_workflow(filename="workflow-local.yaml")
        w = create_workflow()
        Benchmark.Stop()
        g = str(w.graph)
        print(g)
        assert "name: start" in g
        assert "start-job-rivanna.hpc.virginia.edu-3:" in g

        print (w.filename)

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
