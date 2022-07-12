import io
import time

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
from cloudmesh.common.console import Console
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer

class Graph:


    def load(self, filename=None):

        # if filename is not None:
        #    raise NotImplementedError
        # shoudl read from file the graph, but as we do Queues yaml dic
        # we do not need filename read right now
        return
        if filename is None:
            raise ValueError("No file associated with this graph")
        else:
            self.db = ydb(filename=filename)
            data = self.db.load()

        return data


class Workflow:

    def __init__(self, name="workflow", filename=None, user=None, host=None):
        # name, label, user, host, status, progress, command
        # if filename exists, load filename
        # if graph is not None overwrite the graph potentially read from filename
        if filename is None:
            filename = f"~/.cloudmesh/workflow/workflow-{name}"

        self.graph = Graph(name=name, filename=filename)
        self.user = user
        self.host = host



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
        self.graph.load(filename)

    def add(self, filename):
        """
        This method adds another workflow to the existing one. If nodes with the
        same name exists, they will be simply overwritten by the existing nodes

        :param filename:
        :type filename:
        :return:
        :rtype:
        """
        pass

    def save(self, filename):
        # implicitly done when using yamldb
        self.graph.save()
