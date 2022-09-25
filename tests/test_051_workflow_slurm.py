###############################################################
# pytest -v --capture=no tests/test_051_workflow_slurm.py
# pytest -v  tests/test_051_workflow_slurm.py
# pytest -v --capture=no  tests/test_051_workflow_slurm.py::TestWorkflowSlurm::<METHODNAME>
###############################################################
import os
import time
from pathlib import Path
from subprocess import STDOUT, check_output

import networkx as nx
import pytest

from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Console
from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.variables import Variables
from cloudmesh.vpn.vpn import Vpn
from utilities import create_dest

create_dest()

banner(Path(__file__).name, c="#", color="RED")



variables = Variables()

name = "slurm"

host = "rivanna.hpc.virginia.edu"
username = variables["username"]

if username is None:
    Console.error("No username provided. Use cms set username=ComputingID")
    quit()

job = None
job_id = None


try:
    if not Vpn.enabled():
        Console.error('vpn not enabled')
    command = f"ssh {username}@{host} hostname"
    print (command)
    content = Shell.run(command, timeout=3)
    login_success = True
except Exception as e:  # noqa: E722
    print (e)
    login_success = False


run_job = f"run-slurm"
wait_job = f"wait-slurm"

w = None


def create_workflow(filename='workflow-slurm.yaml'):
    global w
    global username
    w = Workflow(filename=filename, load=False)

    localuser = Shell.sys_user()
    login = {
        "localhost": {"user": f"{localuser}", "host": "local"},
        "rivanna": {"user": f"{username}", "host": "rivanna.hpc.virginia.edu"},
        "pi": {"user": f"{localuser}", "host": "red"},
    }

    n = 0

    user = login["rivanna"]["user"]
    host = login["rivanna"]["host"]

    jobkind = 'slurm'

    shell_files = Path(f'{__file__}').as_posix()
    shell_files_dir = Path(os.file.dirname(shell_files)).as_posix()
    runtime_dir = Path(Shell.map_filename(
        '~/.cloudmesh/workflow/workflow-slurm/runtime').path).as_posix()
    os.chdir('workflow-slurm')

    for script in ["start", "end"]:
        Shell.copy(f"{shell_files_dir}/workflow-slurm/{script}.sh", runtime_dir)
        assert os.path.isfile(f"./runtime/{script}.sh")
        w.add_job(name=script, kind=jobkind, user=user, host=host)

    for host, kind in [("rivanna", "slurm")]:
        print("HOST:", host)
        user = login[host]["user"]
        host = login[host]["host"]

        print(n)
        w.add_job(name=f"slurm", kind=kind, user=user, host=host)
        Shell.copy(f"{shell_files}/../workflow-slurm/slurm.sh", runtime_dir)
        # os.system(f"cp ./workflow-slurm/job-{host}-{n}.sh .")
        n = n + 1

        w.add_dependencies(f"slurm,end")
        w.add_dependencies(f"start,slurm")

    print(len(w.jobs) == n)
    g = str(w.graph)
    print(g)
    w.save(filename=filename)
    assert "name: start" in g
    return w

def remove_workflow(filename="workflow-slurm.yaml"):
    # Remove workflow source yaml filr
    Shell.rm(filename)

    # Remove experiment execution directory
    full_dir = Shell.map_filename('~/experiment').path

    Shell.rmdir(full_dir)

    workflow_slurm_dir = Shell.map_filename('~/.cloudmesh/workflow/workflow-slurm').path
    Shell.rmdir(workflow_slurm_dir)

    # logic
    # 1. copy testsdef remove_workflow(filename="workflow.yaml"):
    #     # Remove workflow source yaml filr
    #     Shell.rm(filename)
    #
    #     # Remove experiment execution directory
    #     full_dir = Shell.map_filename('~/experiment').path
    #
    #     # remove locat workflow file, for state notification
    #     Shell.rm("~/.cloudmesh/workflow")
    #
    #     # logic
    #     # 1. copy workflow.yaml to local dir simulation from where we start the workflow
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
    #             'workflow.yaml',
    #             '~/experiment',
    #             "~/.cloudmesh/workflow/workflow",
    #             "~/.cloudmesh/workflow/workflow/workflow.yaml"
    #         ]:
    #             where = Shell.map_filename(filename).path
    #             assert not os.path.exists(where)/workflow.yaml to local dir simulation from where we start the workflow
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
            'scripts/workflow.yaml',
            '~/experiment',
        ]:
            where = Shell.map_filename(filename).path
            assert not os.path.exists(where)


@pytest.mark.incremental
class TestWorkflowSlurm:

    # def test_load_slurm_workflow(self):
    #     HEADING()
    #     global w
    #     Benchmark.Start()
    #     w = Workflow()
    #     w.load("workflow-slurm/slurm-workflow.yaml")
    #     Benchmark.Stop()
    #     print(w.graph)

    def test_set_up(self):
        """
        establishing a queues object, saving 2 queues to it, each with 10 jobs
        :return: no return
        """
        HEADING()
        global w
        global username
        Benchmark.Start()
        # w = Workflow()
        create_dest()
        w = create_workflow("workflow-slurm.yaml")

        Benchmark.Stop()
        # print(len(w.jobs) == n)

    def test_show(self):
        HEADING()
        global w
        if os_is_windows():
            w.graph.save(filename="test-slurm.svg", colors="status", layout=nx.circular_layout, engine="dot")
        else:
            w.graph.save(filename="test-slurm.svg", colors="status", layout=nx.circular_layout, engine="dot")
        # Shell.browser("/tmp/test-slurm.svg")
        # assert os.path.exists("~/tmp/test-slurm.svg") == True

    def test_get_node(self):
        HEADING()
        global w
        Benchmark.Start()
        s1 = w["slurm"]
        s2 = w.job("slurm")
        Benchmark.Stop()
        print(s1)
        assert s1 == s2

    def test_table(self):
        HEADING()
        global w
        Benchmark.Start()
        print(w.table)
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

    @pytest.mark.skipif(not login_success, reason=f"host {username}@{host} not found or VPN not enabled")
    def test_run(self):
        HEADING()
        Benchmark.Start()
        w.run_topo()
        Benchmark.Stop()
        banner("Workflow")
        print(w.graph)

    def test_delete_remnants(self):
        HEADING()
        Benchmark.Start()
        time.sleep(2)
        remove_workflow("workflow-slurm.yaml")

        Benchmark.Stop()


    # def test_run(self):
    #     HEADING()
    #     Benchmark.Start()
    #     w.run_parallel()
    #     Benchmark.Stop()
    #     banner("Workflow")
    #     print(w.graph)
