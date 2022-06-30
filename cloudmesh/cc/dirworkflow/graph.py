import io
from datetime import time

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
from cloudmesh.cc.queue import Job
from cloudmesh.common.console import Console
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer

"""
This class enables to manage dependencies between jobs.
To specifie dependencies we can use a string that includes comma 
separated names of jobs. The workflow can be stored into a yaml file.

g = Graph()
g.edges
g.nodes

g.add_edges("a,b,d")
g.add_edges("a,c,d") # will also add missing nodes

g.add_nodes("a", {"status"="ready"})
g.add_nodes("b", "status"="ready")    # will use dict update not eliminate other fields

g.add_nodes("a,b,d", "status"="ready")
    # will add the nodes, but also update the interanal attributes for the nodes, 
    eg sets state to ready

g.export("a.pdf")

A show function is available that alloew the plotting of nodes with a default layout 
and color values defined by a color map. By default a colormap for status with

ready = white
failed = red
running = blue 
done= green

is used. One has the ability to define color maps for any key that contains strings.

To for example change the status colors you could use

g.set_color("status", 
            {"ready": "green", 
             "failed": "yellow",
             "running": "orange", 
             "done": "white"}
             "other": "grey"
            )

as you can see you can also define colors for otehr values that could be set in this case 
for the node status. To display the graph you can say:

g.show()

"""


class Graph:
    """
    This class creates the customizable graph object with colors and labels and
    such. This graph is the visual representation of the workflow,
    which is created in the workflow class.
    """

    def __init__(self, name="graph", filename=None, flow=None):

        if filename is None:
            self.filename = './cloudmesh/workflow'
        else:
            self.filename = filename

        self.sep = "-"
        self.colors = {}
        self.set_status_colors()
        self.name = name
        self.db = ymdb(filename=self.filename)
        self.nodes = self.db.data['workflow'][flow]['nodes']
        self.edges = self.db.data['workflow'][flow]['edges']

    def create_graph(self):
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.nodes)
        self.graph.add_edges_from(self.edges)

    def set_status_colors(self):
        self.add_color("status",
                       ready="white",
                       done="green",
                       failed="red",
                       running="blue")

    def add_color(self, key, **colors):
        if self.colors is None:
            self.colors = {}
        if key not in self.colors:
            self.colors[key] = {}
        self.colors[key].update(**colors)

    def __str__(self):
        data = {
            "nodes": dict(self.nodes),
            "edges": dict(self.edges),
        }
        if self.colors:
            data["colors"] = dict(self.colors)

        return yaml.dump(data, indent=2)

    def display_graph(self, destination=None):
        color_map = self.get_colors()
        if destination is None:
            destination = self.filename

        nx.draw(self.graph, node_color=color_map, with_labels=True) # need to add colors to this
        for i in range(0, 100):  # need to figure out a better time stamp for this
            plt.show()
            time.sleep(.1)
            plt.close()

    def get_colors(self):
        colors = []
        for job in self.nodes:
            color = self.nodes['status']
            colors.append(colors)














    def add_node(self, name, **data):
        if name not in self.nodes:
            self.nodes[name] = data
        else:
            self.nodes[name].update(**data)
        self.nodes[name]["name"] = name

    def add_edge(self, source, destination, **data):
        #
        # TODO: add dependnecy to attribute in node dependency_in,
        #   dependency_out, we could use a set for that. so multiple
        #   dependencies are ignored
        #
        name = f"{source}{self.sep}{destination}"
        if name not in self.edges:
            self.edges[name] = {
                "source": source,
                "destination": destination,
                "name": name
            }
        self.edges[name].update(**data)

    def set_status(self, name, status):
        self.nodes[name]["status"] = status

    def get_status(self, name):
        self.nodes[name]["status"]

    def add_dependency(self, source, destination):
        self.add_dependencies(self, f"{source},{destination}")

    def add_dependencies(self, dependency, nodedata=None, edgedata=None):
        nodes = Parameter.expand(dependency)
        print(nodes)
        # check if all nodes exists if not create the missing once
        # loop through all node pairs and create adges, as name for adges
        # you use {source}-{destination}
        for node in nodes:
            print(node)
            if nodedata is None:
                self.add_node(node)
            else:
                self.add_node(node, **nodedata)
        for i in range(len(nodes) - 1):
            source = nodes[i]
            destination = nodes[i + 1]
            if edgedata is None:
                self.add_edge(source, destination)
            else:
                self.add_edge(source, destination, **edgedata)

    def rename(self, source, destination):
        """
        renames a name with the name source to destination. The destination
        must not exist. All edges will be renamed accordingly.

        :param source:
        :type source:
        :param destination:
        :type destination:
        :return:
        :rtype:
        """
        pass

    def export(self, filename="show,a.png,a.svg,a.pdf"):
        # comma separated list of output files in one command
        # if show is included show() is used
        pass

        output = Parameter.expand(filename)
        for filename in output:
            if "show" == filename:
                self.show()
            elif filename.endswith(".pdf"):
                pass
            # and so on
