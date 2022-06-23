from cloudmesh.cc.db.yamldb import database as ymdb
from cloudmesh.cc.db.shelve import database as shdb
from cloudmesh.cc.queue import Job
import networkx as nx
from matplotlib import pyplot as plt
from queue import Queue

"""
    This is the workflow class, which will create a graph of nodes(jobs) in the 
    order that is requested by the user of this job queuing service. 

    We are assuming that the dependencies are the jobs that we will be working 
    with. Additionally, the dependencies are a list of the jobs. Therefore, 
    following these specifications, the following methods are built. 

"""


class Workflow:

    def __init__(self, name='workflow', dependencies=None, database=None,
                 scheduler=None):

        self.nodes = dependencies
        self.edges = None
        self.db = self.database(database)
        self.graph = None
        self.flow = None

        if dependencies is not None:
            self.add_nodes(dependencies)
            self.add_edges(dependencies)

    def database(self):
        # checking which type of database there is, so we know which to load
        if self.database.lower() == 'yamldb':
            self.db = ymdb.load()
        elif self.database.lower() == 'shelve':
            self.db = shdb.load()
        else:
            raise ValueError("Not one of the implemented databases")

    def status(self, name):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def add_nodes(self, nodes):
        print(nodes)
        for node in nodes:
            job = Job(name=node)
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
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.nodes)
        self.graph.add_edges_from(self.edges)

    def display(self):
        color_map = []
        for n in self.nodes:
            color_map.append('blue')
        nx.draw(self.graph, node_color=color_map, with_labels=True)
        plt.show()

    # job = Job(name='abc')  can add labels even if they don't exist
    # job.label = 'abc'