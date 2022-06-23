from cloudmesh.cc.db.yamldb import database as ymdb
from cloudmesh.cc.queue import Job

"""
    This is the workflow class, which will create a graph of nodes(jobs) in the 
    order that is requested by the user of this job queuing service. 
"""

class Workflow:

    def __init__(self, name='workflow', dependencies=None, database=None, scheduler=None):

        self.nodes = None
        self.edges = None
        # checking which type of database there is, so we know which to load
        if database.lower() == 'yamldb':
            self.queue = ymdb.get(name)
        elif database.lower() == 'shelve':
            self.queue = shdb.get(name)
        else:
            raise ValueError("Not one of the implemented databases")

        if dependencies is not None:
            self.add_nodes(dependencies)
            self.add_edges(dependencies)

        # creating the workflow
        """
        
        
        
        
        
        if scheduler is None:
            scheduler = 'fifo'
            q = Queue()
            
            for d in dependencies:
                value = self.queue.get(d)
                q.put(value)

            self.nodes = []
            for n in q:
                node = q.get(n)
                self.flow.append(node)

            self.edges = []
            for i in self.nodes - 1:
                edge = (i, i + 1)
                self.edges.append(edge)
        """



    def status(self, name):
        raise NotImplementedError



    def run(self):
        raise NotImplementedError

    def add_nodes(self, nodes):
        print(nodes)
        self.nodes = []
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


    #job = Job(name='abc')  can add labels even if they don't exist
    #job.label = 'abc'










