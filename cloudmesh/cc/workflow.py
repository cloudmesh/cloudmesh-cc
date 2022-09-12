import io
import time

import graphviz
import matplotlib.image as mpimg
import networkx as nx
import yaml
from matplotlib import pyplot as plt
from pprint import pprint
from cloudmesh.common.Shell import Shell
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile
from cloudmesh.common.util import readfile
from pathlib import Path
from yamldb import YamlDB
from cloudmesh.cc.queue import Job
from cloudmesh.common.console import Console
from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import banner
import os
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import is_gitbash
import json
from cloudmesh.cc.labelmaker import Labelmaker
from datetime import datetime
from cloudmesh.common.variables import Variables

if os_is_windows():
    import pygetwindow as gw

"""
This class enables to manage dependencies between jobs.
To specify dependencies we can use a string that includes comma 
separated names of jobs. The workflow can be stored into a yaml file.

g = Graph()
g.edges
g.nodes

g.add_edges("a,b,d")
g.add_edges("a,c,d") # will also add missing nodes

g.add_nodes("a", {"status"="ready"})
g.add_nodes("b", "status"="ready")    # will use dict update not eliminate other fields

g.add_nodes("a,b,d", "status"="ready")
    # will add the nodes, but also update the internal attributes for the nodes, 
    eg sets state to ready

g.export("a.pdf")

A show function is available that allow the plotting of nodes with a default layout 
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

as you can see you can also define colors for other values that could be set in this case 
for the node status. To display the graph you can say:

g.show()

"""


class Graph:
    # this is pseudocode

    def __init__(self, name="graph", filename=None, clear=True):
        """
        initialize the graph with characteristics such as edges, nodes
        and colors
        :param name: name of the graph
        :type name: str
        :param filename: name of the file of the graph
        :type filename: str
        :param clear: whether to reload from scratch
        :type clear: bool
        """

        self.sep = "-"
        self.edges = dotdict()
        self.nodes = dotdict()
        self.colors = None
        self.set_status_colors()
        self.name = name
        self.filename = filename
        self.node_count = 0

        if filename is not None and not clear:
            self.load(filename=filename)
        #
        # maybe
        # config:
        #    name:
        #    colors:

    def clear(self):
        """
        resets the graph characteristics to a clean slate
        :return: nothing
        :rtype: None
        """
        self.sep = "-"
        self.edges = dotdict()
        self.nodes = dotdict()
        self.colors = None
        self.set_status_colors()
        self.name = None
        self.filename = None
        self.node_count = 0

    def __getitem__(self, name):
        """
        returns the specified variable from the nodes
        :param name: the variable to be retrieved
        :type name: str
        :return: the specified variable
        """
        return self.nodes[name]

    def set_status_colors(self):
        """
        adds the ready, undefined, done, failed, and running colors
        as hex values
        :return: nothing
        :rtype: None
        """
        # self.add_color("status",
        #                ready="white",
        #                done="green",
        #                failed="red",
        #                running="blue")
        self.add_color("status",
                       ready="white",
                       undefined="#DBFF33",
                       done="#CCFFCC",
                       failed="#FFCCCC",
                       running='#CCE5FF')

    def add_color(self, key, **colors):
        """
        adds specified color(s)
        :param key: the status whose color will be changed
        :type key: str
        :param colors: the colors to be added
        :type colors: kwargs
        :return: nothing
        :rtype: None
        """
        if self.colors is None:
            self.colors = {}
        if key not in self.colors:
            self.colors[key] = {}
        self.colors[key].update(**colors)

    def __str__(self):
        """
        returns the graph in string format with its
        characteristics and specifications
        :return: graph in string format
        :rtype: str
        """
        data = {
            "nodes": dict(self.nodes),
            "dependencies": dict(self.edges),
        }
        workflow = {'workflow': data}

        if self.colors is not None:
            workflow["colors"] = dict(self.colors)

        return yaml.dump(workflow, indent=2)

    def load(self, filename=None):
        """
        loads a graph for a workflow
        :param filename: the graph to load
        :type filename: str
        :return: nothing
        :rtype: None
        """
        # if filename is not None:
        #    raise NotImplementedError
        # should read from file the graph, but as we do Queues yaml dic
        # we do not need filename read right now

        try:
            self.name = os.path.basename(filename).split(".")[0]
        except Exception as e:
            # Console.error(str(e), traceflag=True)
            self.name = "workflow"
        with open(filename, 'r') as stream:
             graph = yaml.safe_load(stream)

        dependencies = graph["workflow"]["dependencies"]
        nodes = graph["workflow"]["nodes"].items()

        for name, node in nodes:
            if "name" not in node:
                node["name"] = name
            self.add_node(**node)


        for edge in dependencies:
             self.add_dependencies(edge)

    def add_node(self, name, **data):
        """
        adds node(s) to the graph
        :param name: the name of the node
        :type name: str
        :param data: additional information related to node, like status
        :type data: kwargs
        :return: nothing
        :rtype: None
        """
        if name not in self.nodes:
            self.nodes[name] = data
        else:
            self.nodes[name].update(**data)
        self.nodes[name]["name"] = name
        if "label" not in  self.nodes[name]:
            self.nodes[name]["label"] = self.nodes[name]["name"]
        if "format" not in self.nodes[name]:
            self.nodes[name]["format"] = self.nodes[name]["label"]
        if "number" not in self.nodes[name]:
            self.nodes[name]["number"] = self.node_count
            self.node_count += 1

    def add_edge(self, source, destination, **data):
        """
        adds edge(s) to the graph
        :param source: beginning edge
        :type source: str
        :param destination: end edge
        :type destination: str
        :param data: additional information
        :type data: kwargs
        :return: nothing
        :rtype: None
        """
        #
        # TODO: add dependency to attribute in node dependency_in,
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
        if "parent" not in self.nodes[destination]:
            self.nodes[destination]["parent"] = []
        if "parent" not in self.nodes[source]:
            self.nodes[source]["parent"] = []
        self.nodes[destination]["parent"].append(source)

    def done(self, parent):
        """
        removes from all nodes the names parent
        :param parent: originating node
        :type parent: str
        :return: nothing
        :rtype: None
        """
        for name in self.nodes:
            if "parent" in self.nodes[name]:
                if parent in self.nodes[name]["parent"]:
                    self.nodes[name]["parent"].remove(parent)

    def todo(self):
        """
        finds all nodes with no parents and progress != 100

        :return: list of node names with no parents
        :rtype: list
        """
        result = []
        for name in self.nodes:
            try:
                if self.nodes[name]["progress"] != 100 and \
                        self.nodes[name]["parent"] is None:
                    result.append(name)
            except Exception as e:  # noqa: E722
                pass
        return result

    def set_status(self, name, status):
        """
        sets the status of a specified node
        :param name: node whose status will be changed
        :type name: str
        :param status: name of status to be set for the node
        :type status: str
        :return: nothing
        :rtype: None
        """
        self.nodes[name]["status"] = status

    def get_status(self, name):
        """
        retrieves status of a specified node
        :param name: node whose status will be retrieved
        :type name: str
        :return: the status of the node
        :rtype: str
        """
        return self.nodes[name]["status"]

    def add_dependency(self, source, destination):
        """
        adds a dependency for a node. a dependency enforces
        the completion of a previous node in order for the
        next to be run
        :param source: beginning node
        :type source: str
        :param destination: node that cannot run without the source
        :type destination: str
        :return: nothing
        :rtype: None
        """
        self.add_dependencies(self, f"{source},{destination}")

    def add_dependencies(self, dependency, nodedata=None, edgedata=None):
        """
        adds dependencies for nodes. a dependency enforces
        the completion of a previous node in order for the
        next to be run
        :param dependency: a comma separated string with names of nodes
        :type dependency: str
        :param nodedata: specifications of the node such as status
        :type nodedata: kwargs
        :param edgedata: specifications of the edge
        :type edgedata: kwargs
        :return: nothing
        :rtype: None
        """
        nodes = Parameter.expand(dependency)
        # check if all nodes exists if not create the missing once
        # loop through all node pairs and create adges, as name for adges
        # you use {source}-{destination}
        for node in nodes:
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
        """
        takes the inputted filename, expands it into list
        if commas and brackets are present, and saves the
        graph into specified filenames. this function seems
        to be incomplete
        :param filename: names to save the graph to. if show, then shows graph
        :type filename: str
        :return: nothing
        :rtype: None
        """
        # comma separated list of output files in one command
        # if show is included show() is used

        output = Parameter.expand(filename)
        for filename in output:
            if "show" == filename:
                self.show()
            elif filename.endswith(".pdf"):
                pass
            # and so on

    def save_to_file(self, filename, exclude=None):
        """
        saves the graph to a specified filename and
        excludes nodes if exclude is specified.
        meant to be used to save as yaml, not svg.
        :param filename: name of file to save graph to
        :type filename: str
        :param exclude: nodes to exclude from the saved file
        :type exclude: str
        :return: nothing
        :rtype: None
        """
        # exclude parent
        location = os.path.dirname(filename)
        if len(location) > 0:
            os.makedirs(location, exist_ok=True)

        if exclude is not None:
            g = Graph()
            g.nodes = self.nodes
            g.edges = self.edges
            for name, node in g.nodes.items():
                try:
                    for attribute in exclude:
                        del node[attribute]
                except:
                    pass
            content = str(g)
        else:
            content = str(self)

        writefile(filename=filename, content=content)

    def create_label(self, name):
        """
        creates the text to appear on a node in the graph
        :param name: name of node to add text to
        :type name: str
        :return: the text that will appear on node in string format
        :rtype: str
        """
        label = None
        if "label_format" in self.nodes[name]:
            label = self.nodes[name]["label_format"]
        elif "label" in self.nodes[name]:
            label = self.nodes[name]["label"]
        if label is None:
            label = name
        replacement = Labelmaker(label)
        msg = replacement.get(**self.nodes[name])
        return msg

    def save(self,
             filename="test.svg",
             colors=None,
             layout=nx.spring_layout,
             engine="networkx"):
        """
        generates and saves the graph
        :param filename: file to save the graph to
        :type filename: str
        :param colors: colors to use for the graph
        :type colors:
        :param layout: layout of the graph
        :type layout:
        :param engine: name of engine to use to draw graph
        :type engine: str
        :return: nothing
        :rtype: None
        """
        dot = graphviz.Digraph(comment='Dot Graph')
        dot.attr('node', shape="box")

        graph = nx.DiGraph()

        color_map = []

        for name, e in self.nodes.items():
            if colors is None:
                msg = self.create_label(name)
                graph.add_node(name)
                dot.node(name, color='white', label=msg)
                color_map.append('white')
            else:
                value = e[colors]
                color_map.append(self.colors[colors][value])
                if name in ["start", "end"]:
                    shape = "diamond"
                else:
                    shape = "box"
                msg = self.create_label(name)
                self.nodes[name]["label"] = msg

                dot.node(name,
                         label=msg,
                         # color=self.colors[colors][value],
                         style=f'filled,rounded',
                         shape=shape,
                         fillcolor=self.colors[colors][value])

        for name, e in self.edges.items():
            graph.add_edge(e["source"], e["destination"])
            dot.edge(e["source"], e["destination"])

        if engine == "dot":
            basefilename = os.path.basename(filename)
            prefix, ending = basefilename.split(".")
            dot_filename = prefix + ".dot"
            dot_filename = os.path.join(os.path.dirname(filename), dot_filename)
            writefile(dot_filename, str(dot.source))
            os.system(f"dot -T{ending} {dot_filename} -o {filename}")

        elif engine == "graphviz":
            pos = layout(graph)
            nx.draw(graph, with_labels=True, node_color=color_map, pos=pos)
            plt.axis('off')
            plt.savefig(filename)

        elif engine == 'pyplot':

            # generate dot graph
            P = nx.nx_pydot.to_pydot(graph)

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

    def get_topological_order(self): #get_sequentil_order
        """
        returns a list of the topological order of the workflow
        :return: list depicting the workflow
        :rtype: list
        """
        tuples = []
        for name, edge in self.edges.items():
            tuples.append((edge["source"], edge["destination"]))
        g = nx.DiGraph(tuples)
        order = list(nx.topological_sort(g))
        return order

    def create_topological_order(self): #create_sequential_order
        # or put it in workflow or in both # mey need to be in workflow.
        """
        update the graph while each node bget a number determined from get_sequential_order
        :return: list depicting the workflow
        :rtype: list
        """
        order = self.get_topological_order()
        i = 0
        for name in order:
            self.nodes[name]["number"] = i
            i = i + 1
        return order


class Workflow:
    """
    Workflow documentation

    w = Workflow(filename="workflow.yaml")
    w.load(filename="abc.yaml") <- loads in the graph, but will save it still to workflow.yaml
    w.add(filename="add.yaml") <-adds a new workflow into the existing one.
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

    def __init__(self,
                 name=None,
                 filename=None, # original workflow
                 runtime_dir=None, # this is where the images are store, as well as the yml file when we run it
                 user=None,
                 host=None,
                 load=True):
        """
        initializes workflow with specified characteristics
        :param name: name of workflow
        :type name: str
        :param filename: location of yaml file to load workflow from
        :type filename: str
        :param user: name of user
        :type user: str
        :param host: location of where the workflow will be run
        :type host: str
        :param load: whether to load the workflow
        :type load: bool
        """
        # name, label, user, host, status, progress, command
        # if filename exists, load filename
        # if graph is not None, overwrite the graph potentially read from filename
        # gvl reimplemented but did not test
        # The workflow is run in experiment/workflow

        #
        # name may not be defined properly
        #


        cms_variables = Variables()
        try:
            if name is None and filename is not None:
                self.name = os.path.basename(filename).split(".")[0]
            else:
                self.name = name or 'workflow'
        except:
            self.name = 'workflow'

        # self.filename is the filename wherever it is located

        # self.original = f"~/.cloudmesh/workflow/{name}/{name.yaml}"
        # if self.filenme != self.original:
        #   cp self.filename self.original

        self.runtime_dir = runtime_dir or f"~/.cloudmesh/workflow/{name}/runtime"
        self.runtime_filename = f"{self.runtime_dir}/{name.yaml}"


        # self.filename = filename or f"~/.cloudmesh/workflow/{self.name}/{self.name}.yaml"
        if not filename:
            self.filename = f"~/.cloudmesh/workflow/{self.name}/{self.name}.yaml"
        else:
            self.filename = filename
        self.filename = path_expand(self.filename)
        Shell.mkdir(os.path.dirname(self.filename))
        # Shell.mkdir(os.path.dirname(self.runtime_dir))

        try:
            self.name = os.path.basename(filename).split(".")[0]
        except Exception as e:
            print(e)
            self.name = "workflow"

        self.user = user
        self.host = host

        try:
            print("Workflow Filename:", self.filename)
            self.graph = Graph(name=name, filename=filename)
            # gvl added load but not tested
            if load:
                self.load(self.filename)
        except Exception as e:  # noqa: E722
            Console.error(e, traceflag=True)
            pass

        self.created_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        cms_created_name = 'created_time_' + self.name
        cms_variables.__setitem__(
            cms_created_name, self.created_time)

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


    def __str__(self):
        """
        returns workflow and its characteristics in string format
        :return: string format of workflow
        :rtype: str
        """
        return str(self.graph)

    @property
    def jobs(self):
        """
        retrieves the jobs of the workflow
        :return: the jobs that belong to the workflow
        :rtype: dotdict
        """
        return self.graph.nodes  # [name]

    def __getitem__(self, name):
        """
        returns the details of an item within the workflow
        :param name: name of item
        :type name: str
        :return: details of an item within the workflow
        :rtype: dict
        """
        return self.jobs[name]

    def job(self, name):
        """
        returns the details of a job within the workflow
        :param name: name of job
        :type name: str
        :return: details of a job within the workflow
        :rtype: dict
        """
        return self.jobs[name]

    @property
    def dependencies(self):
        """
        retrieves the dependencies of the workflow
        :return: the dependencies of the workflow
        :rtype: dotdict
        """
        # gvl implemented but not tested
        return self.graph.edges  # [name]

    def predecessor(self, name):
        """
        retrieves the jobs that must be run before the specified job
        (the pre-requisites)
        :param name: name of a job
        :type name: str
        :return: list of preceding jobs
        :rtype: list
        """
        # GVL reimplemented but not tested
        predecessors = []
        edges = self.dependencies

        for _name, edge in edges.items():
            if edge["destination"] == name:
                predecessors.append(edge["source"])
        return predecessors

    def get_predecessors(self, name):
        """
        figure out all the dependencies of the name node
        then test if each node in front (parent) has progress of 100
        if the parent has progress 100, remove those nodes
        :param name: name of a job
        :type name: str
        :return: list of preceding jobs
        :rtype: list
        """
        parents = []
        candidates = self.predecessor(name)
        for candidate in candidates:

            if self.job(candidate)['progress'] != 100:
                parents.append(candidate)

        if parents == []:
            return None
        else:
            return parents

    def save_with_state(self, filename, stdout=False):
        """
        save the workflow with state
        :param filename: which file to save the workflow
        :type filename: str
        :param stdout: if True then return the output
        :type stdout: bool
        :return: if stdout is True then returns the string of yaml dump
        :rtype: None or str
        """
        # print(self.graph)
        data = {}
        data['workflow'] = {
            "nodes": dict(self.graph.nodes),
            "dependencies": dict(self.graph.edges),
        }
        if self.graph.colors:
            data["colors"] = dict(self.graph.colors)

        d = str(yaml.dump(data, indent=2))
        writefile(filename, d)
        if stdout:
            return d

    def load_with_state(self, filename):
        """
        load the workflow with state
        :param filename: which file to load the workflow from
        :type filename: str
        :return: nothing
        :rtype: None
        """
        s = readfile(filename)
        data = yaml.safe_load(s)
        if "nodes" in data['workflow']:
            self.graph.nodes = data['workflow']['nodes']
        if "dependencies" in data['workflow']:
            self.graph.edges = data['workflow']['dependencies']
        if "colors" in data:
            self.graph.colors = data['colors']

    def load(self, filename, clear=True):
        """
        Loads a workflow graph from file. However, the file is still stored in
        the filename that was used when the Workflow was created. This allows to
        load in a saved workflow in another file, but continue working on it in
        the file used in init

        :param filename: which file to load the workflow from
        :type filename: str
        :param clear: whether to clear workflow. not implemented
        :type clear: bool
        :return: nothing
        :rtype: None
        """
        # self.graph.load(...)
        """ 
        workflow:
          nodes:
            a:
               name: a
               user: gregor
               host: localhost
               kind: local
               status: ready
               label: job-1-label
               script: test-a.sh
            b:
               name: b
               user: gregor
               host: localhost
               kind: local
               status: ready
               label: job-2-label
               script: test-a.sh
          dependencies:
            - a,b
        """

        self.graph = Graph()
        # if not clear:
        self.graph.load(filename=filename)

        # with open(filename, 'r') as stream:
        #     graph = yaml.safe_load(stream)
        #
        # dependencies = graph["workflow"]
        #nodes = graph["workflow"]["nodes"].items()
        #
        # # for name, node in graph["workflow"]["nodes"].items():
        for name, node in self.graph.nodes.items():
             if "name" not in node:
                 node["name"] = name
             self.add_job(**node)
        #
        # for edge in dependencies:
        #     self.add_dependencies(edge)


        # expand script and exec and save shell scripts
        for name, node in self.graph.nodes.items():
            if node['exec'] is None and node['script'] is not None:
                del node['exec']
            if "exec" in node and node["kind"] == "local":
                from cloudmesh.cc.job.localhost.Job import Job
                if "script" not in node:
                    node["script"] = f"{name}.sh"
                job = Job.create(filename=node['script'], exec=node["exec"])

    def save(self, filename):
        """
        save the workflow
        :param filename: where to save the workflow
        :type filename: str
        :return: nothing
        :rtype: None
        """
        if os_is_windows():
            name = os.path.basename(filename).replace(r".yaml", "")
            dir = Shell.map_filename(fr"~/.cloudmesh/workflow/{name}/{name}.yaml").path
            self.graph.save_to_file(dir)
        self.graph.save_to_file(filename)

    def add_job(self,
                name=None,
                user=None,
                host=None,
                label=None,
                label_format=None,
                kind="local",
                status="ready",
                progress=0,
                script=None,
                exec=None,
                pid=None,
                **kwargs
                ):
        """
        add a job to the workflow
        :param name: name of job
        :type name: str
        :param user: username for job
        :type user: str
        :param host: where the job will be run
        :type host: str
        :param label: what the node will say on the graph
        :type label: str
        :param label_format: how the label will be formatted in the graph
        :type label_format:
        :param kind: the type of job, such as local, ssh, slurm
        :type kind: str
        :param status: how the job is doing, like ready, failed, done
        :type status: str
        :param progress: a number from 0 to 100 that reports job completeness
        :type progress: int
        :param script: the script that the job will run
        :type script: str
        :param exec: how the job will be executed
        :type exec: str
        :param pid: process id of the job
        :type pid: int or str
        :param kwargs: any other miscellaneous specifications for the job
        :type kwargs: kwargs
        :return: nothing
        :rtype: None
        """

        label = label or name
        user = user or self.user or Shell.user()
        host = host or self.host or Shell.host()
        label_format = label_format or label or name

        if script is None:
            script = f"{name}.sh"

        now = str(DateTime.now())
        self.graph.add_node(
            name=name,
            label=label,
            label_format=label_format,
            kind=kind,
            user=user,
            host=host,
            status=status,
            progress=progress,
            created=now,
            modified=now,
            script=script,
            exec=exec,
            instance=None
        )
        self.save(self.filename)

    def add_dependency(self, source, destination):
        """
        add a job dependency to the workflow (and the graph)
        :param source: job to be completed first
        :type source: str
        :param destination: job to be completed after the source
        :type destination: str
        :return: nothing
        :rtype: None
        """
        self.graph.add_dependency(source, destination)

    def add_dependencies(self, dependency):
        """
        add a job dependency to the workflow (and the graph)
        :param dependency: the dependency to be added
        :type dependency: str
        :return: nothing
        :rtype: None
        """
        self.graph.add_dependencies(dependency=dependency)

    def update_status(self, name, status):
        """
        manually update a job's status
        :param name: the job whose status will be updated
        :type name: str
        :param status: the new status to be set for the job
        :type status: str
        :return: nothing
        :rtype: None
        """
        self.graph[name]["status"] = status

    def set_progress(self, name, percent):
        """
        manually update a job's progress
        :param name: name of the job
        :type name: str
        :param percent: value from 0 to 100 for the progress
        :type percent: int
        :return: nothing
        :rtype: None
        """
        self.graph[name]["progress"] = percent

    def update_progress(self, name):
        """
        manually update the progress of a job according to its log file
        :param name: name of job
        :type name: str
        :return: nothing
        :rtype: None
        """
        # fetches log file and looks for progress event TBD
        # once progress is fetched set it for the named job
        raise NotImplementedError

    def run_parallel(self,
                     directory="~/experiment",
                     order=None,
                     dryrun=False,
                     show=True,
                     period=0.5,
                     filename=None):
        """
        run a workflow in a parallel fashion
        :param directory: where the workflow should be run
        :type directory: str
        :param order: how the jobs should be run chronologically
        :type order:
        :param dryrun: if true then the workflow isn't really run. for testing
        :type dryrun: bool
        :param show: whether to show graph as workflow is run
        :type show: bool
        :param period: how long to wait after showing the graph
        :type period: float
        :param filename: where to save the graph
        :type filename: str
        :return: nothing
        :rtype: None
        """
        finished = False

        undefined = []
        completed = []  # list of completed nodes
        running = []  # list of running nodes
        outstanding = list(self.jobs)  # list of outstanding nodes
        failed = []  # list of failed nodes

        def info():
            """
            gives information about the jobs of the workflow
            :return: nothing
            :rtype: None
            """
            print("Undefined:   ", undefined)
            print("Completed:   ", completed)
            print("Running:     ", running)
            print("Outstanding: ", outstanding)
            print("Failed:      ", failed)
            print()
            print("Todo:        ", self.graph.todo())
            print("Dependencies:", len(self.graph.edges))

        def update(name):
            """
            update the jobs status and progress
            :param name: name of job
            :type name: str
            :return: nothing
            :rtype: None
            """
            banner(f"update {name}")
            log = self.jobs[name]["instance"].get_log()
            status = self.jobs[name]["instance"].get_status()
            progress = self.jobs[name]["instance"].get_progress()
            self.jobs[name]['status'] = status
            self.jobs[name]['progress'] = progress

            # print("Job data", name, status, progress)

            if progress == 100:
                self.graph.done(name)
                if name in running:
                    running.remove(name)
                if name not in completed:
                    completed.append(name)
                if name in undefined:
                    undefined.remove(name)

            elif status == "undefined":
                if name in running:
                    running.remove(name)
                if name not in completed:
                    completed.append(name)
                if name not in undefined and name not in outstanding:
                    undefined.append(name)
            # elif status == 'running':
            #    ready.remove(name)

        def start(name):
            """
            runs the job
            :param name: name of job
            :type name: str
            :return: nothing
            :rtype: None
            """
            banner(name)

            job = self.job(name=name)
            wf_name = os.path.basename(filename).split(".")[0]
            experiment_directory = f'~/experiment/{wf_name}/{name}'
            job['directory'] = experiment_directory
            if not dryrun and job["status"] in ["ready"]:
                local = wsl = ssh = slurm = lsf = False
                if job['kind'] in ["local"]:
                    local = True
                    from cloudmesh.cc.job.localhost.Job import Job
                elif job['kind'] in ["wsl"]:
                    wsl = True
                    from cloudmesh.cc.job.wsl.Job import Job
                elif job['kind'] in ['ssh']:
                    ssh = True
                    from cloudmesh.cc.job.ssh.Job import Job
                elif job['kind'] in ['slurm']:
                    slurm = True
                    from cloudmesh.cc.job.slurm.Job import Job
                elif job['kind'] in ['lsf']:
                    lsf = True
                    from cloudmesh.cc.job.lsf.Job import Job
                else:
                    from cloudmesh.cc.job.localhost.Job import Job
                job["status"] = "running"
                name = job['name']
                host = job['host']
                username = job['user']
                label = name
                if local or wsl:
                    job["instance"] = Job(name=name,
                                          host=host,
                                          username=username,
                                          label=label,
                                          directory=experiment_directory)
                if ssh or slurm:
                    job = Job(name=name,
                              host=host,
                              username=username,
                              label=label,
                              directory=experiment_directory)
                    job.sync()
                    job.run()
                if local or wsl:
                    job["instance"].sync()
                    job["instance"].run()
                    # print(str(job["instance"]))
                    running.append(name)
                    outstanding.remove(name)

                # elif job['kind'] in ["local-slurm"]:
                #     raise NotImplementedError
                # elif job['kind'] in ["remote-slurm"]:
                #     raise NotImplementedError
            else:
                # banner(f"Job: {name}")
                Console.msg(f"running {name}")

        if os_is_windows():
            Shell.mkdir("./tmp")
            filename = filename or "tmp/workflow.svg"
        else:
            filename = filename or "/tmp/workflow.svg"

        first = True

        while not finished:

            info()

            for name in running:
                update(name)

            todo = self.graph.todo()

            for name in todo:
                print("TODO", name)
                start(name)

            # print(self.table)
            print(self.table2(with_label=True))

            if show:
                self.graph.save(filename=filename, colors="status", engine="dot")
                if first and os_is_mac():
                    Shell.open(filename=filename)
                    first = False
                elif first and os_is_linux():
                    Shell.open(filename=filename)
                else:
                    Shell.browser(filename)
                    if os_is_windows():
                        win = gw.getWindowsWithTitle('MINGW64:')
                        win.activate()

            time.sleep(period)
            finished = len(completed) == len(self.jobs)

            # debugging
            #info()
            #input()

        # save graph occurs again to make sure things are being saved
        self.graph.save(filename=filename,
                        colors="status",
                        engine="dot")

    def run_topo(self,
                 order=None,
                 dryrun=False,
                 show=True,
                 filename=None):
        """
        runs the workflow in a topological fashion
        :param order: how the jobs should be run chronologically
        :type order:
        :param dryrun: if true then the workflow isn't really run. for testing
        :type dryrun: bool
        :param show: whether to show the graph as workflow is run
        :type show: bool
        :param filename: where the graph should be saved
        :type filename: str
        :return: nothing
        :rtype: None
        """
        # bug the tno file needs to be better handled
        if order is None:
            order = self.sequential_order

        if os_is_windows() and filename is None:
            Shell.mkdir("./tmp")
            filename = filename or f"tmp/{self.name}.svg"
        else:
            filename = filename or f"/tmp/{self.name}.svg"

        first = True
        for name in order():
            job = self.job(name=name)

            if not dryrun:
                local = wsl = ssh = slurm = lsf = False
                if job['kind'] in ["local"]:
                    local = True
                    from cloudmesh.cc.job.localhost.Job import Job
                elif job['kind'] in ["wsl"]:
                    wsl = True
                    from cloudmesh.cc.job.wsl.Job import Job
                elif job['kind'] in ['ssh']:
                    ssh = True
                    from cloudmesh.cc.job.ssh.Job import Job
                elif job['kind'] in ['slurm']:
                    slurm = True
                    from cloudmesh.cc.job.slurm.Job import Job
                elif job['kind'] in ['lsf']:
                    lsf = True
                    from cloudmesh.cc.job.lsf.Job import Job
                else:
                    from cloudmesh.cc.job.localhost.Job import Job
                if local or ssh or slurm:
                    job["status"] = "running"
                name = job['name']
                label_format = job['label_format']
                host = job['host']
                username = job['user']
                label = name
                _job = Job(name=name,
                           host=host,
                           username=username,
                           label=label,
                           label_format=label_format)
                _job.sync()
                _job.run()

                if local or wsl or slurm:
                    _job.watch(period=0.5)
                elif ssh or slurm:
                    _job.watch(period=3)

                self.graph.done(name)
                print(self.table)
                _job.watch(period=1)
                log = _job.get_log()
                status = _job.get_status()
                progress = _job.get_progress()
                if progress == 100:
                    status = "done"
                print('Status: ', status)
                print('Progress: ', progress)
                self.jobs[name]['status'] = status
                self.jobs[name]['progress'] = progress

                # elif job['kind'] in ["local-slurm"]:
                #     raise NotImplementedError
                # elif job['kind'] in ["remote-slurm"]:
                #     raise NotImplementedError
            else:
                # banner(f"Job: {name}")
                Console.msg(f"running {name}")

            if show:
                for name in self.graph.nodes:
                    msg = self.graph.create_label(name)
                    self.graph.nodes[name]["label"] = msg

                self.graph.save(filename=filename,
                                colors="status",
                                layout=nx.circular_layout,
                                engine="dot")

                if first and os_is_mac():
                    Shell.open(filename=filename)
                    first = False
                elif os_is_linux():
                    #  elif first and os_is_linux():
                    #Shell.open(filename=filename)  # does not work
                    os.system(f"chromium {filename}&")
                    #os.system(f"eog {filename}")

                else:
                    Shell.browser(filename)
                    time.sleep(0.1)
                    # if os_is_windows():
                    #
                    #     #import win32gui
                    #     #import win32con
                    #
                    #     #hwnd = win32gui.FindWindowEx(None, None, None,
                    #     #                             'MINGW64:')
                    #     # def getShell():
                    #     #     thelist = []
                    #     #
                    #     #     def findit(hwnd, ctx):
                    #     #         if 'MINGW64:' in win32gui.GetWindowText(
                    #     #                 hwnd):  # check the title
                    #     #             thelist.append(hwnd)
                    #     #     win32gui.EnumWindows(findit, None)
                    #     #     return thelist
                    #     # b = getShell()
                    #     # win32gui.SetWindowPos(b[0], win32con.HWND_TOPMOST,
                    #     #                       100,
                    #     #                       100, 200, 200, 0x0001 | 0x0002)
                    #     #the following works
                    #     if is_gitbash():
                    #         win = gw.getWindowsWithTitle('MINGW64:')[0]
                    #         win.activate()



    def display(self, filename=None, name='workflow', first=True):
        """
        show the graph of the workflow
        :param filename: location of the graph
        :type filename: str
        :param name: name of the workflow to be displayed
        :type name: str
        :param first: if True then this is first time graph is displayed
        :type first: bool
        :return: nothing
        :rtype: None
        """
        if os_is_windows():
            Shell.mkdir("./tmp")
            filename = filename or f"tmp/{name}.svg"
        else:
            filename = filename or f"/tmp/{name}.svg"
        self.graph.save(filename=filename, colors="status", engine="dot")
        if first and os_is_mac():
            os.system(f'open {filename}')
            first = False
        elif first and os_is_linux():
            os.system(f'gopen {filename}')
        else:
            cwd = os.getcwd()
            os.system(f'start chrome {cwd}\\{filename}')

    def create_topological_order(self): #create_sequential_order
        # or put it in workflow or in both # mey need to be in workflow.
        """
        update the graph while each node bget a number determined from get_sequential_order
        :return: list depicting the workflow
        :rtype: list
        """
        # tuples = []
        # for name, edge in self.graph.edges.items():
        #     tuples.append((edge["source"], edge["destination"]))
        # g = nx.DiGraph(tuples)
        # order = list(nx.topological_sort(g))
        # return order

        # detrmon the order based on nodes and edges using toposort
        # itterate through the order (nwmaes, ids), and set the no to thedopological soort
        # for i in self.get_sequential_order():
        #   node[top[i]]["number"] = i
        pass

    def sequential_order(self): #get_sequentil_order
        """
        returns a list of the topological order of the workflow
        :return: list depicting the workflow
        :rtype: list
        """
        tuples = []
        for name, edge in self.graph.edges.items():
            tuples.append((edge["source"], edge["destination"]))
        g = nx.DiGraph(tuples)
        order = list(nx.topological_sort(g))
        return order

    @property
    def yaml(self):
        """
        returns a yaml dump of the nodes and dependencies of the workflow
        :return: yaml dump of workflow as string
        :rtype: str
        """
        data = {
            'nodes: ': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return yaml.dump(data)

    @property
    def dict_of_workflow(self):
        """
        returns a dict of the nodes and dependencies of the workflow
        :return: dict of workflow
        :rtype: dict
        """
        data = {
            'nodes: ': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return data

    def json(self, filepath=None):
        """
        returns the workflow as json string
        :param filepath: where the file is located
        :type filepath: str
        :return: a json string of the workflow
        :rtype: str
        """
        data = {
            'nodes: ': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return json.dumps(data, indent=2)

    @property
    def table(self):
        """
        returns a table of the workflow
        :return: a table of the workflow
        :rtype: None or PrettyTable or str or dict
        """
        # gvl rewritten
        with_label = True

        data = dict(self.graph.nodes)

        for name in self.graph.nodes:
            msg = self.graph.create_label(name)
            data[name]["label"] = msg

        if with_label:
            order = ['host',
                     'status',
                     'label',
                     'label_format',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']
        else:
            order = ['host',
                     'status',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']

        return Printer.write(self.graph.nodes,
                             order=order)

    def table2(self, with_label=False):
        """
        returns a table of the workflow
        :param with_label: whether to include label in table
        :type with_label: bool
        :return: a table of the workflow
        :rtype: None or PrettyTable or str or dict
        """
        # gvl rewritten
        # with_label = False

        data = dict(self.graph.nodes)

        for name in self.graph.nodes:
            label = self.graph.nodes[name]["label"]
            msg = self.graph.create_label(name)
            data[name]["label"] = msg

        if with_label:
            order = ['host',
                     'status',
                     'label',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']
        else:
            order = ['host',
                     'status',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']

        return Printer.write(self.graph.nodes,
                             order=order)

    def remove_workflow(self):
        """
        deletes workflow from the local file system
        :return: nothing
        :rtype: None
        """
        # gvl rewritten
        # TODO: the rm seems wrong
        d = os.path.dirname(self.filename)
        os.system(f"rm -r {d}")
        self.graph = None
        self.jobs = None
        self.graph.edges = None

    def remove_job(self, name, state=False):
        """
        removes a particular job from the workflow
        :param name: name of job to be removed from workflow
        :type name: str
        :param state: whether to save workflow with state after job removal
        :type state: bool
        :return: nothing
        :rtype: None
        """
        # del self.jobs[name]
        p = self.jobs.pop(name)
        # print("popped:",p)

        # remove dependencies to job
        dependencies = self.graph.edges.items()

        dellist = []
        for edge, dependency in dependencies:
            if dependency["source"] == name or dependency["destination"] == name:
                dellist.append(edge)

        # TODO: remove parent node
        for key in dellist:
            self.graph.edges.pop(key)

        if state:
            self.save_with_state(self.filename)
        else:
            self.save(self.filename)

    def status(self):
        """
        returns details of the workflow in dict format
        :return: details of workflow in dict format
        :rtype: dict
        """
        # gvl implemented but not tested
        s = "done"
        _status = {"workflow": s,
                   "jobs": {}}
        for name in self.jobs:
            state = self.jobs[name]["status"]
            progress = self.jobs[name]["progress"]
            _status["jobs"][name] = {
                "status": state,
                "progress": progress
            }
            if state in ["running"]:
                s = "running"
            elif state in ["undefined"]:
                s = "undefined"
            elif state in ["failed"]:
                s = "failed"
            elif state in ["ready"]:
                s = "ready"
        _status["workflow"] = s
        return _status
