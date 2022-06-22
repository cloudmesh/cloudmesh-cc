import networkx
from cloudmesh.cc import queue
from cloudmesh.cc.db.yamldb import database as ymdb
from cloudmesh.cc.db.shelve import database as shdb


"""
    This is the workflow class, which will create a graph of nodes(jobs) in the 
    order that is requested by the user of this job queuing service. 
"""

class workflow:

    def __init__(self, name, dependencies, database):

        if database.lower() == 'yamldb':
            self.queue = ymdb.get(name)
        elif database.lower() == 'shelve':
            self.queue = shdb.get(name)
        else:
            raise ValueError("Not one of the implemented databases")

        self.db.get



    def status(self):

    def


