import io
import time
from pprint import pprint

import graphviz
import matplotlib.image as mpimg
import networkx as nx
import yaml
from matplotlib import pyplot as plt

from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from pathlib import Path
from cloudmesh.cc.db.yamldb import database as ydb
from cloudmesh.cc.queue import Job
from cloudmesh.common.console import Console
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import banner
import os
from cloudmesh.common.systeminfo import os_is_linux, os_is_mac, os_is_windows
import json
from cloudmesh.common.Printer import PrettyTable
from cloudmesh.common.Printer import Printer



class Workflow:

    def save(self):
        # implicitly done when using yamldb
        self.graph.save_to_file(filename=self.filename)


    def run_parallel(self, order=None, parallel=False, dryrun=False, show=True, period=0.5):
        finished = False

        undefined = []
        completed = [] # list of completed nodes
        running = [] # list of runiing nodes
        outstanding = list(self.jobs)  # list of outstanding nodes
        failed = [] # list of failed nodes

        def info():
            print ("Undefined:  ", undefined)
            print ("Completed:  ", completed)
            print ("Running:    ", running)
            print ("Outstanding:", outstanding)
            print ("Failed:     ", failed)
            print ("Ready:      ", self.graph.todo())

        def update(name):
            banner(f"update {name}")
            log = self.jobs[name]["instance"].get_log()
            status = self.jobs[name]["instance"].get_status()
            progress = self.jobs[name]["instance"].get_progress()
            self.jobs[name]['status'] = status
            self.jobs[name]['progress'] = progress
            print(status, progress)
            if progress == 100:
                running.remove(name)
                completed.append(name)
                self.graph.done(name)
                if name in undefined:
                    undefined.remove(name)
            elif status == "undefined":
                running.remove(name)
                undefined.append(name)

        def start(name):
            banner(name)

            job = self.job(name=name)
            if not dryrun and job["status"] in ["ready"]:
                if job['kind'] in ["local"]:
                    from cloudmesh.cc.job.localhost.Job import Job as local_Job
                    job["status"] = "running"
                    name = job['name']
                    host = job['host']
                    username = job['user']
                    label = name

                    job["instance"] = local_Job(name=name,
                                                host=host,
                                                username=username,
                                                label=label)
                    job["instance"].sync()
                    job["instance"].run()
                    print(str(job["instance"]))
                    running.append(name)
                    outstanding.remove(name)

                elif job['kind'] in ["ssh"]:
                    print(job)
                    from cloudmesh.cc.job.ssh.Job import Job as ssh_job
                    name = job['name']
                    host = job['host']
                    username = job['user']
                    label = name
                    remote_job = ssh_job(name=name, host=host,
                                         username=username, label=label)
                    remote_job.sync()
                    remote_job.run()
                # elif job['kind'] in ["local-slurm"]:
                #     raise NotImplementedError
                # elif job['kind'] in ["remote-slurm"]:
                #     raise NotImplementedError
            else:
                # banner(f"Job: {name}")
                Console.msg(f"running {name}")

        while not finished:

            info()

            for name in running:
                update(name)

            todo = self.graph.todo()

            for name in todo:
                print("TODO", name)
                start(name)

            print(self.table)

            if show:
                filename = "/tmp/a.svg"
                self.graph.save_picture(filename=filename, colors="status",
                                layout=nx.circular_layout, engine="dot")
                if os_is_mac():
                    os.system(f'open {filename}')
                elif os_is_linux():
                    os.system(f'gopen {filename}')
                else:
                    Shell.browser(filename='a.png')
            time.sleep(period)
            finished = len(completed) == len(self.jobs)

            # input("ENTER")





    def remove_job(self, name):
        # gvl rewritten by gregor not tested
        # remove job
        del self.jobs[name]

        # remove dependencies to job
        dependencies = self.graph.edges.items()
        for edge, dependency in list(dependencies):
            if dependency["source"] == name or dependency["destination"] == name:
                del self.graph.edges[edge]

        self.save()



    def list_dependencies(self):
        edges = self.dependencies
        return Printer.dict(edges)

