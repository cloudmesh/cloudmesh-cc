import networkx
from cloudmesh.cc import queue
from cloudmesh.cc.db.yamldb import database as ymdb
from cloudmesh.cc.db.shelve import database as shdb
from queue import Queue


"""
    This is the workflow class, which will create a graph of nodes(jobs) in the 
    order that is requested by the user of this job queuing service. 
"""

class workflow:

    def __init__(self, name, dependencies, database, scheduler=None):

        # checking which type of database there is, so we know which to load
        if database.lower() == 'yamldb':
            self.queue = ymdb.get(name)
        elif database.lower() == 'shelve':
            self.queue = shdb.get(name)
        else:
            raise ValueError("Not one of the implemented databases")

        # creating the workflow
        if scheduler is None:
            scheduler = 'fifo'
            q = Queue()

            for d in dependencies:
                value = queue.get(d)
                q.put(value)

            self.nodes = []
            for n in q:
                node = q.get(n)
                self.flow.append(node)

            self.edges = []
            for i in self.nodes - 1:
                edge = (i, i + 1)
                self.edges.append(edge)



    def status(self):

    def


