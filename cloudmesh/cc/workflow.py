import networkx as nx
from matplotlib import pyplot as plt
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell

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
            self.add_nodes_names()
            self.add_edges()

    def status(self, name):
        return name['status']

    def run(self):
        self.counter = 0
        for name in range(0, len(self.graph)):
            c = self.nodes[name]['command']
            r = Shell.run(c)
            self.counter = self.counter + 1
            print(r)
            #self.db.data['queue'][self.name]['output'] = r

    def add_nodes(self, name):
        self.db.load()
        for j in self.dependencies:
            job = self.db.get_job(self.name, j)
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
        #plt.savefig(f'{filename}digraph.png')
        plt.show()

    # job = Job(name='abc')  can add labels even if they don't exist
    # job.label = 'abc'