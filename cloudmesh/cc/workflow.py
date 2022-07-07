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
from cloudmesh.cc.queue import Job
from cloudmesh.common.console import Console
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import banner
import os

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

    def __init__(self, name="graph", filename=None):
        self.sep = "-"
        self.edges = dotdict()
        self.nodes = dotdict()
        self.load(filename=filename)
        self.colors = {}
        self.set_status_colors()
        self.name = name
        #
        # maybe
        # config:
        #    name:
        #    colors:

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

    def save(self, filename="test.svg", colors=None, layout=nx.spring_layout,
             engine="networkx"):
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
        # name, label, user, host, status, progress, command
        # if filename exists, load filename
        # if graph is not None overwrite the graph potentially read from filename
        if filename is None:
            filename = f"~/.cloudmesh/workflow/workflow-{name}"

        self.graph = Graph(name=name, filename=filename)
        self.user = user
        self.host = host

        # should this go into graph?
        # if Path.exists(filename):
        #    self.workflow = self.load(filename)
        # else:
        #    directory = path_expand(filename)
        #    Shell.mkdir(directory)
        #    self.data = {}
        #    self.save()

        # self.workflow = {}  # the overall workflow dictionary will have both jobs and dependencies

        # self.label = None

    @property
    def jobs(self):
        return self.graph.nodes  # [name]

    def __getitem__(self, name):
        return self.jobs[name]

    def job(self, name):
        return self.jobs[name]

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
        # self.graph.load(...)
        pass

    def predecessor(self, name):
        
        raise NotImplementedError


    def get_parents(self, name):
        """
        figure out all of the dependencies of the name node
        then test if each node in front (parent) has progress of 100
        if the parent has progress 100, remove those nodes
        :return:
        """
        parents = []
        candidates = self.predecessors(name)
        print(candidates)
        for candidate in candidates:
            if candidate['progress'] != 100:
                parents.append(candidate)

        if parents == []:
            return None
        else:
            return parents



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

    def add_job(self,
                name=None,
                user=None,
                host=None,
                label=None,
                kind="local",
                status="ready",
                progress=0,
                pid=None
                ):

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

        now = DateTime.now()
        self.graph.add_node(
            name=name,
            label=label,
            kind=kind,
            user=user,
            host=host,
            status=status,
            progress=progress,
            created=now,
            modified=now
        )

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

    def run(self, order=None, parallel=False, dryrun=False, show=True):

        if order is None:
            order = self.sequential_order

        for name in order():
            job = self.job(name=name)
            if not dryrun:
                if job['kind'] in ["local"]:
                    from cloudmesh.cc.job.localhost.Job import Job as local_Job
                    name = job['name']
                    host = job['host']
                    username = job['user']
                    label = name
                    localhost_job = local_Job(name=name, host=host,
                                              username=username, label=label)
                    localhost_job.sync()
                    localhost_job.run()
                    localhost_job.watch(period=0.5)
                    status = localhost_job.get_status()
                    progress = localhost_job.get_progress()
                    banner(name)
                    print(str(localhost_job))
                    print('Status: ', status)
                    print('Progress: ', progress)
                    self.jobs[name]['status'] = status
                    self.jobs[name]['progress'] = progress
                elif job['kind'] in ["ssh"]:
                    print(job)
                    from cloudmesh.cc.job.ssh.Job import Job as ssh_job
                    name = job['name']
                    host = job['host']
                    username = job['user']
                    label = name
                    remote_job = ssh_job(name=name, host=host,
                                         username=username, label=label)
                    remote_job.sync()
                    remote_job.run()
                # elif job['kind'] in ["local-slurm"]:
                #     raise NotImplementedError
                # elif job['kind'] in ["remote-slurm"]:
                #     raise NotImplementedError
            else:
                # banner(f"Job: {name}")
                Console.msg(f"running {name}")

            if show:
                self.graph.save(filename="/tmp/a.svg", colors="status",
                                layout=nx.circular_layout, engine="dot")
                # Shell.browser(filename='/tmp/a.pdf')
                os.system('open /tmp/a.svg')
                # time.sleep(3)

    def sequential_order(self):
        tuples = []
        for name, edge in self.graph.edges.items():
            print(edge["source"], edge["destination"])
            tuples.append((edge["source"], edge["destination"]))
        g = nx.DiGraph(tuples)
        order = list(nx.topological_sort(g))
        print(order)
        return order

    @property
    def yaml(self):
        # print the workflow as text use yaml.dump
        pass

    def json(self):
        # print as json dump
        pass

    @property
    def table(self):
        return Printer.write(self.graph.nodes)
        pass


