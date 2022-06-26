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
    # this is pseudocode

    def __init__(self, filename=None):
        self.sep = "-"
        self.edges = dotdict()
        self.nodes = dotdict()
        self.load(filename=filename)
        self.colors = {}
        self.set_status_colors()

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

    def load(self, filename=None):
        if filename is not None:
            raise NotImplementedError
            # shoudl read from file the graph, but as we do Queues yaml dic
            # we do not need filename read right now

    def add_node(self, name, **data):
        if name not in self.nodes:
            self.nodes[name] = data
        else:
            self.nodes[name].update(**data)
        self.nodes[name]["name"] = name

    def add_edge(self, source, destination, **data):
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

    def save(self, filename="test.svg", colors=None, layout=nx.spring_layout, engine="networkx"):
        dot = graphviz.Digraph(comment='Dot Graph')
        graph = nx.DiGraph()
        color_map = []
        for name, e in self.nodes.items():
            if colors is None:
                graph.add_node(name)
                dot.node(name, color='white')
                color_map.append('white')
            else:
                value = e[colors]
                color_map.append(self.colors[colors][value])
                dot.node(name, color=self.colors[colors][value])

        for name, e in self.edges.items():
            graph.add_edge(e["source"], e["destination"])
            dot.edge(e["source"], e["destination"])

        if engine == "dot":

            prefix, ending = filename.split(".")
            dot_filename = prefix + ".dot"
            writefile(dot_filename, str(dot.source))
            if ".dot" not in filename:
                Shell.run(f"dot -T{ending} {dot_filename} -o {filename}")

        elif engine == "graphviz":
            pos = layout(graph)
            nx.draw(graph, with_labels=True, node_color=color_map, pos=pos)
            plt.axis('off')
            plt.savefig(filename)

        elif engine == 'pyplot':

            # generate dot graph
            P = nx.nx_pydot.to_pydot(graph)
            print(P)

            # convert from `networkx` to a `pydot` graph
            pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)

            # render the `pydot` by calling `dot`, no file saved to disk
            png_str = pydot_graph.create_png(prog='dot')

            # treat the DOT output as an image file
            sio = io.BytesIO()
            sio.write(png_str)
            sio.seek(0)
            img = mpimg.imread(sio)

            # plot the image
            imgplot = plt.imshow(img, aspect='equal')
            plt.axis('off')
            plt.savefig(filename)


class Workflow2:

    def __init__(self, name=None, filename=None):
        # if filename exists, load filename
        # if graph is not None overwrite the graph potentially read from filename

        pass

    def load(self, filename):
        pass

    def add(self, filename):
        pass

    def save(self, filename):
        # implicitly done when using yamldb
        pass

    def add_job(self,
                name,
                label,
                user,
                host,
                status,
                progress,
                command
                ):
        pass

    def add_dependencies(self, dependency):
        pass

    def set_status(self, name, status):
        pass

    def run(self, order=None, parallel=False):

        if order == None:
            order = self.order

        # now runn in order


    def sequential_order(self):
        order = list(nx.topological_sort(self.graph))
        return order

    @property
    def table(self):
        # print the table use cloudmesh table printer
        pass

    @property
    def yaml(self):
        # print the workflow as texttable use yaml.dump
        pass

    def json(self):
        # print as json dump
        pass

class Workflow:

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
