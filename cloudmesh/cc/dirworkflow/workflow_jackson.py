import io

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
from cloudmesh.cc.db.yamldb.database import Database as ymdb
from cloudmesh.common.console import Console
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.cc.job.localhost.Job import Job as local_Job
from cloudmesh.cc.job.ssh.Job import Job as ssh_Job
from cloudmesh.cc.dirworkflow.graph import Graph


class Workflow:
    """
    Workflow doocumentation

    w = Workflow(filename="workflow.yaml")
    w.load(filename="abc.yaml") <- loads in teh graph, but will save it still to workflow.yaml
    w.add(filename="add.yaml") <-adds a new worflow into the existing one.
    w.add_job(name="a",
                command="hostname",
                user=None, # bug if kind is local and user is None, we do not need user, but can take local user
                host=None, # bug:  if host is none and kind is local use localhost
                label="a",
                kind="local",
                status="ready",
                progress=0)
    w.add_job(name="b", command="ls")
    w.add_job(name="c", command="pwd")
    w.add_job(name="d", command="uname -a")
    w.add_dependencies(dependency="a,b,d")
    w.add_dependencies(dependency="a,c,d")

    w.run()


    """

    def __init__(self, name="workflow", filename=None, user=None, host=None):
        """
        The workflow object is the larger data structure that holds the jobs,
        then creates the graph based on the dependency flow.

        an example yamldb file should look like this:

        workflow:

            jobs:
                [job1,job2,job3,job4]

            ***each of these job objects holds all the necessary information in
            order to run everything***

            flow1:
                [job1,job3,job2]

            flow2:
                [job1,job2,job3]
            flow3:
                [job3,job2,job1]

        So then when something is run, it is simply looking for the jobs in the
        yaml database, and those jobs can be called upon and manipulated as pleased
        into different flows and merges of flows. I call this, user accessibility.

        Workflow relies upon the job classes for the localhost and ssh host. These
        are objects. They also have really great (and tested) running and
         status capabilities.

        Workflow does the following things: sets up the file, sets up the database
        allows users to see the status of a flow, allows users to get specific
        jobs within flows,

        :param name:
        :param filename:
        :param user:
        :param host:
        :param dependencies:
        """
        if filename is None:
            self.filename = f"~/.cloudmesh/workflow/workflow-{name}"
        else:
            self.filename=filename

        self.db = ymdb(name='Workflow', filename='~/.cloudmesh/workflow')
        self.db.data['jobs'] = []
        self.name = name
        self.db.save()

    @property
    def jobs(self):
        return self.db.data['jobs']

    def __getitem__(self, name):
        return self.jobs[name]

    def get_job(self, name):
        job = self.db.data['workflow']['jobs'][name]
        return job

    def load(self, filename):
        """
        Loads a workflow graph from file. However the file is still stored in
        the filename that was used when the Workflow was created. This allows to
        load in a saved workflow in another file, but continue working on it in
        the file used in init

        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        data = self.db.load(filename=self.filename)
        return data

    def add_job(self,
                name=None,
                user=None,
                host=None,
                label=None,
                ):

        # setting up the fields for the job:

        label = label or name
        user = user or self.user
        host = host or self.host
        defined = True
        if name is None:
            defined = False
            Console.error("name is None")
        if user is None:
            defined = False
            Console.error("user is None")
        if host is None:
            defined = False
            Console.error("host is None")
        if not defined:
            raise ValueError("user or host not specified")

        # targeting which type of job it is and appending it to the list of jobs
        if host == 'localhost':
            job = local_Job(name=name, username=user, host=host, label=label)
            self.db.data['jobs'].append(job)

        elif host == 'rivanna':
            job = ssh_Job(name=name, username=user, host=host, label=label)
            self.db.data['jobs'].append(job)
        else:
            raise NotImplementedError

    def create_flow(self, name, dependencies):
        """
        the dependencies are a list of the names of jobs. We want to access those
        jobs and create a list of nodes of those jobs.
        :return:
        """
        nodes = []
        edges = []

        for name in dependencies:
            job = self.get_job(name)
            job['status'] = 'yellow'
            nodes.append(job)

        for name in dependencies - 1:
            tuple = (dependencies[name], dependencies[name + 1])
            edges.append(tuple)

        self.load()
        self.db.data['workflow'][name]['nodes'] = nodes
        self.db.data['workflow'][name]['edges'] = edges

    def create_graph(self, name, flow):
        nodes = self.db.data['workflow'][flow]['nodes']
        edges = self.db.data['workflow'][flow]['edges']
        graph = Graph(filename=self.filename, nodes=nodes, edges=edges)
        self.db.data['workflow'][name] = graph

    def save(self, filename):
        # implicitly done when using yamldb
        self.db.data.save(filename=self.filename)


    def run(self, name):
        nodes = self.db.data['workflow'][name]['nodes']

        for job in nodes:
            job['status'] = 'blue'
            job.run()

    @property
    def table(self):
        return Printer.write(self.graph.nodes)
        pass





class rest:



    def add_dependency(self, source, destination):
        self.graph.add_dependency(source, destination)

    def add_dependencies(self, dependency):
        self.graph.add_dependencies(dependency=dependency)

    def update_status(self, name, status):
        self.graph[name]["status"] = status

    def set_progress(self, name, percent):
        pass

    def update_progress(self, name):
        # fetches log file and looks for progress event TBD
        # once progress is fetched set it for the named job
        pass

    @property
    def yaml(self):
        # print the workflow as texttable use yaml.dump
        pass

    def json(self):
        # print as json dump
        pass




class Workflow_old:

    def __init__(self,
                 name=None,
                 dependencies=None,
                 database=None,
                 filename=None):
        """
        :param name: name of the queue we are loading jobs in from
        :param dependencies: list of the jobs to append as the nodes of the graph
        :param database: the type of the database that we are pulling the queue and dependencies from
        :param filename: the name of the file that the database is in
        """

        # unsorted nodes and edges
        self.nodes = []
        self.nodes_names = []
        self.edges = []
        self.graph = None

        # nodes and edges that are sorted
        self.sorted_nodes = []
        self.sorted_edges = []
        self.sorted_graph = None

        # the two other fields we need for this OOP class
        self.dependencies = dependencies
        self.name = name
        self.counter = 0
        self.stat = {}

        if database.lower() == 'yamldb':
            from cloudmesh.cc.db.yamldb.database import Database as QueueDB
        elif database.lower() == 'shelve':
            from cloudmesh.cc.db.shelve.database import Database as QueueDB
        else:
            raise ValueError(
                "This database is not supported for Queues, please fix.")

        if filename is None:
            filename = path_expand("~/.cloudmesh/queue/queues")

        self.db = QueueDB(
            filename=filename)  # now we have access to the correct database

        if dependencies is not None:
            self.add_nodes(name)
            self.add_nodes_names()
            self.add_edges()

        # setting up the database to save the nodes and all that jazz
        if 'workflow' not in self.db.data:
            self.db.data['workflow'] = {}
            self.db.data['workflow'][self.name] = {}
        else:
            self.db.data['workflow'][self.name] = {}

    def update_status(self):
        self.stat = {}
        for job in self.nodes:
            name = job['name']
            s = job['status']
            print(name, s)
            self.stat[name] = s

    def display_status(self):
        for job in self.stat:
            print(job, self.stat[job])

    def get_status(self, name):
        for job in self.stat:
            if name == job:
                return self.stat[job]

    def run(self):
        self.counter = 0
        for name in range(0, len(self.graph)):
            self.nodes[name]['color'] = 'yellow'
            self.nodes[name]['status'] = 'submitted'
            c = self.nodes[name]['command']
            r = Shell.run(c)
            self.nodes[name]['color'] = 'blue'
            self.nodes[name]['status'] = 'running'
            #
            # bug process error depends on jon
            #
            if "CheckProcessError" in r:
                self.nodes[name]['color'] = 'red'
                self.nodes[name]['status'] = 'failed'
            else:
                self.nodes[name]['color'] = 'green'
                self.nodes[name]['status'] = 'done'

            self.counter = self.counter + 1
            print(r)
            self.db.data['workflow'][self.name]['output'] = r

    def add_nodes(self, name):
        self.db.load()
        for j in self.dependencies:
            job = self.db.get_job(self.name, j)
            job['status'] = 'ready'
            job['color'] = 'white'
            self.nodes.append(job)

    def add_edges(self):
        for i in range(0, len(self.nodes_names) - 1):
            edge = (self.nodes_names[i], self.nodes_names[i + 1])
            self.edges.append(edge)

    def add_nodes_names(self):
        for node in self.nodes:
            name = node['name']
            self.nodes_names.append(name)

    def get_node(self, name):
        for node in self.nodes:
            if node["name"] == name:
                return node
        return None

    def create_graph(self, filename=None):
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.nodes_names)
        self.graph.add_edges_from(self.edges)

    def create_sorted_graph(self):
        # first sort the graph then add the sorted edges and nodes
        self.sort_graph()
        print(self.sorted_nodes)
        print(self.sorted_edges)
        self.sorted_graph = nx.DiGraph
        self.sorted_graph.add_nodes_from(self.sorted_nodes)
        self.sorted_graph.add_edges_from(self.sorted_edges)

    def sort_graph(self):
        self.sorted_nodes = list(nx.topological_sort(self.graph))
        for i in range(0, len(self.sorted_nodes) - 1):
            edge = (self.sorted_nodes[i], self.sorted_nodes[i + 1])
            self.sorted_edges.append(edge)

    def display(self, color=None, filename=None):
        # establishing where the graph will go
        # if filename is None:
        #    filename = "~/cloudmesh/cc/images/"

        # setting the color
        if color is None:
            color = 'lightblue'

        color_map = []
        for n in self.nodes_names:
            color_map.append(color)
        nx.draw(self.graph, node_color=color_map, with_labels=True)
        # plt.savefig(f'{filename}digraph.png')
        plt.show()

    # job = Job(name='abc')  can add labels even if they don't exist
    # job.label = 'abc'
