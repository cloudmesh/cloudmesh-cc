import networkx as nx
from matplotlib import pyplot as plt
from cloudmesh.common.util import path_expand

"""
    This is the workflow class, which will create a graph of nodes(jobs) in the 
    order that is requested by the user of this job queuing service. 

    We are assuming that the dependencies are the jobs that we will be working 
    with. Additionally, the dependencies are a list of the jobs. Therefore, 
    following these specifications, the following methods are built. 

    Also, we are loading the jobs from the yaml database that we created. Because
    that is how the service works. 
"""


class Workflow:

    def __init__(self, name=None, dependencies=None, database=None,
                 filename=None, scheduler=None):

        self.nodes = []
        self.edges = None
        self.db = self.database(database)
        self.graph = None
        self.flow = None

        if name is not None:
            self.name = name
        else:
            self.name = 'local'

        if database.lower() == 'yamldb':
            from cloudmesh.cc.db.yamldb.database import Database as QueueDB
        elif database.lower() == 'shelve':
            from cloudmesh.cc.db.shelve.database import Database as QueueDB
        else:
            raise ValueError("This database is not supported for Queues, please fix.")

        if filename is None:
            filename = path_expand("~/.cloudmesh/queue/queues")

        self.db = QueueDB(filename=filename)  # now we have access to the correct database

        if dependencies is not None:
            self.add_nodes(name)
            self.add_edges()

    def status(self, name):
        job = self.db.get_job(self.name, name)
        status = job['status']
        return status

    def run(self):
        for job in self.graph:
            c = job["command"]
            


    def add_nodes(self, name):
        self.db.load()
        for j in self.dependencies:
            job = self.db.get_job(self.name, name)
            print(job)
            self.nodes.append(job)

    def add_edges(self, edges):
        print(edges)
        self.edges = []
        for i in range(0, self.nodes - 1):
            edge = (edges[i], edges[i + 1])
            self.edges.append(edge)

    def get_node(self, name):
        for node in self.nodes:
            if node["name"] == name:
                return node

        return None

    def create_graph(self):
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.nodes)
        self.graph.add_edges_from(self.edges)
        self.graph = list(nx.topological_sort(self.graph))


    def display(self):
        color_map = []
        for n in self.nodes:
            color_map.append('blue')
        nx.draw(self.graph, node_color=color_map, with_labels=True)
        plt.show()

    # job = Job(name='abc')  can add labels even if they don't exist
    # job.label = 'abc'