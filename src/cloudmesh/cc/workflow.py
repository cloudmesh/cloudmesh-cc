"""Cloudmesh Workflow.

This class enables to manage dependencies between jobs.
To specify dependencies we can use a string that includes comma
separated names of jobs. The workflow can be stored into a yaml file::

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
and color values defined by a color map. By default a colormap for status with::

    ready = white
    failed = red
    running = blue
    done= green

is used. One has the ability to define color maps for any key that contains strings.

To for example change the status colors you could use::

    g.set_color("status",
                {"ready": "green",
                 "failed": "yellow",
                 "running": "orange",
                 "done": "white"}
                 "other": "grey"
                )

as you can see you can also define colors for other values that could be set in this case
for the node status. To display the graph you can say::

    g.show()

"""
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


class Graph:
    """The Graph class handles the generation of workflow diagrams."""

    def __init__(self, name="graph", filename=None, clear=True):
        """Initialize the graph with characteristics such as edges, nodes and colors.

        Args:
            name (str): name of the graph
            filename (str): name of the file of the graph
            clear (bool): whether to reload from scratch
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
        """Reset the graph characteristics to a clean slate.

        Returns:
            None: nothing
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
        """Return the specified variable from the nodes.

        Args:
            name (str): the variable to be retrieved

        Returns:
            the specified variable
        """
        return self.nodes[name]

    def set_status_colors(self):
        """Add the ready, undefined, done, failed, and running colors as hex values.

        Returns:
            None: nothing
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
        """Add specified color(s).

        Args:
            key (str): the status whose color will be changed
            **colors (kwargs): the colors to be added

        Returns:
            None: nothing
        """
        if self.colors is None:
            self.colors = {}
        if key not in self.colors:
            self.colors[key] = {}
        self.colors[key].update(**colors)

    def __str__(self):
        """Return the graph in string format.

        Returns:
            str: graph in string format
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
        """Load a graph for a workflow.

        Args:
            filename (str): the graph to load

        Returns:
            None: nothing
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
        """Add node(s) to the graph.

        Args:
            name (str): the name of the node
            **data (kwargs): additional information related to node,
                like status

        Returns:
            None: nothing
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
        """Add edge(s) to the graph.

        Args:
            source (str): beginning edge
            destination (str): end edge
            **data (kwargs): additional information

        Returns:
            None: nothing
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

    def delete_edge(self, source, destination):
        """Add edge(s) to the graph.

        Args:
            source (str): beginning edge
            destination (str): end edge

        Returns:
            None: nothing
        """
        #
        # TODO: add dependency to attribute in node dependency_in,
        #   dependency_out, we could use a set for that. so multiple
        #   dependencies are ignored
        #
        name = f"{source}{self.sep}{destination}"

        del self.edges[name]

        # TODO: do this somehow e.g. remove source from destination in parent
        # if "parent" not in self.nodes[destination]:
        #     self.nodes[destination]["parent"] = []
        # if "parent" not in self.nodes[source]:
        #     self.nodes[source]["parent"] = []
        # self.nodes[destination]["parent"].append(source)

    def delete_node(self, name):

        pass
        # del self.node[name]
        # for all nodes:
        #     if parents of node containes name:
        #         remove the name from parents:

    def done(self, parent):
        """Remove from all nodes the named parent.

        Args:
            parent (str): originating node

        Returns:
            None: nothing
        """
        for name in self.nodes:
            if "parent" in self.nodes[name]:
                if parent in self.nodes[name]["parent"]:
                    self.nodes[name]["parent"].remove(parent)

    def todo(self):
        """Find all nodes with no parents and progress != 100.

        Returns:
            list: list of node names with no parents
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
        """Set the status of a specified node.

        Args:
            name (str): node whose status will be changed
            status (str): name of status to be set for the node

        Returns:
            None: nothing
        """
        self.nodes[name]["status"] = status

    def get_status(self, name):
        """Retrieve status of a specified node.

        Args:
            name (str): node whose status will be retrieved

        Returns:
            str: the status of the node
        """
        return self.nodes[name]["status"]

    def add_dependency(self, source, destination):
        """Add dependency between source and destination.

        Add a dependency for a node. a dependency enforces
        the completion of a previous node in order for the
        next to be run.

        Args:
            source (str): beginning node
            destination (str): node that cannot run without the source

        Returns:
            None: nothing
        """
        self.add_dependencies(self, f"{source},{destination}")

    def add_dependencies(self, dependency, nodedata=None, edgedata=None):
        """Add multiple dependencies betwee several nodes.

        Add dependencies for nodes. a dependency enforces
        the completion of a previous node in order for the
        next to be run.

        An example is a,b,c,d which creates dependencies between
        a,b
        b,c
        c,d
        e.g. a->b->c->d

        Args:
            dependency (str): a comma separated string with names of
                nodes
            nodedata (kwargs): specifications of the node such as status
            edgedata (kwargs): specifications of the edge

        Returns:
            None: nothing
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
        """Export the graph.

        Take the inputted filename, expands it into list
        if commas and brackets are present, and saves the
        graph into specified filenames. this function seems
        to be incomplete.

        Args:
            filename (str): names to save the graph to. if show, then
                shows graph

        Returns:
            None: nothing
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

    def save_to_yaml(self, filename, exclude=None):
        """Save the graph.

        Save the graph to a specified filename and
        excludes nodes if exclude is specified.
        meant to be used to save as yaml, not svg.

        Args:
            filename (str): name of file to save graph to
            exclude (str): nodes to exclude from the saved file

        Returns:
            None: nothing
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
        """Create the text to appear on a node in the graph.

        Args:
            name (str): name of node to add text to.

        Returns:
            str: the text that will appear on node in string format
        """
        label = None
        if "label_format" in self.nodes[name]:
            label = self.nodes[name]["label_format"]
        elif "label" in self.nodes[name]:
            label = self.nodes[name]["label"]
        if label is None:
            label = name
        replacement = Labelmaker(label, self.name, name)
        msg = replacement.get(**self.nodes[name])
        return msg

    def save(self,
             filename="test.svg",
             colors=None,
             layout=nx.spring_layout,
             engine="networkx"):
        """Generate and saves the graph.

        Args:
            filename (str): file to save the graph to
            colors: colors to use for the graph
            layout: layout of the graph
            engine (str): name of engine to use to draw graph

        Returns:
            None: nothing
        """
        dot = graphviz.Digraph(comment='Dot Graph')
        # dot.attr(rankdir='LR')
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
                shape = "box"
                if 'shape' in self.nodes[name]:
                    shape = self.nodes[name]['shape']
                elif name in ["start", "end"]:
                    shape = "diamond"
                else:
                    shape = "box"
                msg = self.create_label(name)
                self.nodes[name]["label"] = msg

                style = 'filled,rounded'
                if 'style' in self.nodes[name]:
                    style = self.nodes[name]['style']
                    if style == '':
                        style = 'filled'

                dot.node(name,
                         label=msg,
                         # color=self.colors[colors][value],
                         style=style,
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
        """Return a list of the topological order of the workflow.

        Returns:
            list: list depicting the workflow
        """
        tuples = []
        for name, edge in self.edges.items():
            tuples.append((edge["source"], edge["destination"]))
        g = nx.DiGraph(tuples)
        order = list(nx.topological_sort(g))
        return order

    def create_topological_order(self): #create_sequential_order
        """Update the graph while each node bget a number determined from get_sequential_order.

        Returns:
            list: list depicting the workflow
        """
        # or put it in workflow or in both # mey need to be in workflow.

        order = self.get_topological_order()
        i = 0
        for name in order:
            self.nodes[name]["number"] = i
            i = i + 1
        return order


class Workflow:
    """Workflow class that runs all jobs, handles dependencies, etc.

    ::

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
                 load=False,
                 clear_runtime_dir=True,
                 runtime=False):
        """Initialize a workflow with specified characteristics.

        Args:
            name (str): name of workflow
            filename (str): location of yaml file to load workflow from
            runtime_dir (str): directory of yaml file to be read and
                written to
            user (str): name of user
            host (str): location of where the workflow will be run
            load (bool): whether to load the workflow
        """
        # name, label, user, host, status, progress, command
        # if filename exists, load filename
        # if graph is not None, overwrite the graph potentially read from filename
        # gvl reimplemented but did not test
        # The workflow is run in experiment/workflow

        #
        # name may not be defined properly
        #

        try:
            if name is None and filename is not None:
                self.name = os.path.basename(filename).split(".")[0]
            else:
                self.name = name or 'workflow'
        except:
            self.name = 'workflow'

        # self.filename is the filename wherever it is located

        # self.filename = filename or f"~/.cloudmesh/workflow/{self.name}/{self.name}.yaml"
        if not filename:
            self.filename = f"~/.cloudmesh/workflow/{self.name}/{self.name}.yaml"
        else:
            self.filename = filename
        self.filename = path_expand(self.filename)
        Shell.mkdir(os.path.dirname(self.filename))
        try:
            self.name = os.path.basename(self.filename).split(".")[0]
        except Exception as e:
            print(e)
            self.name = "workflow"

        self.runtime_dir = runtime_dir or path_expand(
            f"~/.cloudmesh/workflow/{self.name}/runtime/")

        # reset the runtime dir if it exists.
        # if clear_runtime_dir:
        #     if os.path.isdir(self.runtime_dir):
        #         Shell.rmdir(self.runtime_dir)
        if not os.path.isdir(self.runtime_dir):
            Shell.mkdir(self.runtime_dir)
        self.runtime_filename = f"{self.runtime_dir}{self.name}.yaml"
        self.times_filename = f"{self.runtime_dir}{self.name}.dat"
        try:
            if not os.path.isfile(self.runtime_filename):
                Shell.copy(self.filename, self.runtime_filename)
        except:
            pass
        try:
            if not os.path.isfile(self.times_filename):
                writefile(self.times_filename, '')
        except:
            pass

        try:
            print("Workflow Filename:", self.filename)
            if not load:
                self.graph = Graph(name=name, filename=self.runtime_filename)
            else:
                self.graph = Graph(name=name, filename=self.filename)
            # gvl added load but not tested
            if runtime:
                pass
            if not runtime:
                self.load(self.filename)
        except Exception as e:  # noqa: E722
            Console.error(e, traceflag=True)
            pass

        self.created_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        times_dict = yaml.safe_load(
            Path(self.times_filename).read_text())
        if times_dict is None:
            times_dict = {}
        if 'times' in times_dict:
            if 'created_time' not in times_dict['times']:
                times_dict['times']['created_time'] = self.created_time
                d = str(yaml.dump(times_dict, indent=2))
                writefile(self.times_filename, d)
        else:
            times_dict.setdefault('times', {})[
                'created_time'] = self.created_time
            d = str(yaml.dump(times_dict, indent=2))
            writefile(self.times_filename, d)

        self.user = user
        self.host = host

        self.create_topological_order()
        self.graph.save_to_yaml(self.runtime_filename)

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
        """Return workflow and its characteristics in string format.

        Returns:
            str: string format of workflow
        """
        return str(self.graph)

    @property
    def jobs(self):
        """Retrieve the jobs of the workflow.

        Returns:
            dotdict: the jobs that belong to the workflow
        """
        return self.graph.nodes  # [name]

    def __getitem__(self, name):
        """Return the details of an item within the workflow.

        Args:
            name (str): name of item

        Returns:
            dict: details of an item within the workflow
        """
        return self.jobs[name]

    def job(self, name):
        """Return the details of a job within the workflow.

        Args:
            name (str): name of job

        Returns:
            dict: details of a job within the workflow
        """
        return self.jobs[name]

    @property
    def dependencies(self):
        """Retrieve the dependencies of the workflow.

        Returns:
            dotdict: the dependencies of the workflow
        """
        # gvl implemented but not tested
        return self.graph.edges  # [name]

    def predecessor(self, name):
        """Retrieve the jobs that must be run before the specified job.

        Args:
            name (str): name of a job

        Returns:
            list: list of preceding jobs
        """
        # GVL reimplemented but not tested
        predecessors = []
        edges = self.dependencies

        for _name, edge in edges.items():
            if edge["destination"] == name:
                predecessors.append(edge["source"])
        return predecessors

    def get_predecessors(self, name):
        """Return the predecessors.

        Figure out all the dependencies of the name node
        then test if each node in front (parent) has progress of 100
        if the parent has progress 100, remove those nodes.

        Args:
            name (str): name of a job

        Returns:
            list: list of preceding jobs
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
        """Save the workflow with state.

        Args:
            filename (str): which file to save the workflow
            stdout (bool): if True then return the output

        Returns:
            None or str: if stdout is True then returns the string of
            yaml dump
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
        """Load the workflow with state.

        Args:
            filename (str): which file to load the workflow from

        Returns:
            None: nothing
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
        """Load the workflow.

        Load a workflow graph from file. However, the file is still stored in
        the filename that was used when the Workflow was created. This allows to
        load in a saved workflow in another file, but continue working on it in
        the file used in init.

        Args:
            filename (str): which file to load the workflow from
            clear (bool): whether to clear workflow. not implemented

        Returns:
            None: nothing
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
            self.add_job(filename=self.runtime_filename, **node)
        #
        # for edge in dependencies:
        #     self.add_dependencies(edge)


    def save(self, filename=None):
        """Save the workflow.

        Args:
            filename (str): where to save the workflow

        Returns:
            None: nothing
        """
        # if os_is_windows():
        #     name = os.path.basename(filename).replace(r".yaml", "")
        #     dir = Shell.map_filename(fr"~/.cloudmesh/workflow/{name}/{name}.yaml").path
        #     self.graph.save_to_yaml(dir)
        if filename:
            # do not use runtime dir, use experiment dir
            # i forgot about exeriment dir
            # reason experimentdir is noce is that its alos on remote machines

            # we need to be able to set this

            # .cloudmesh/workflow/workflow_a/jobs/workflow_a.yaml

            # cloudmesh:
            #    workflow:
            #       localhost:
            #         name: workflow_a
            #         source: ~/a.yaml
            #         runtime_dir: "~/.cloudmesh/workflow/{cloudmesh.workflow.name}/runtime"
            #         yaml: f"{runtime_dir}/{cloudmesh.workflow.name}.yaml"
            #       rivanna: ???? eg experiment on remote host must be written somewhere,
            #                             for now we can yuos use ~
            #         name: workflow_a
            #         source: ~/a.yaml
            #         runtime_dir: "~/.cloudmesh/workflow/{cloudmesh.workflow.name}/runtime"
            #         yaml: f"{runtime_dir}/{cloudmesh.workflow.name}.yaml"

        # old
            # experiment/workflow_a/jobs/workflow_a.yaml
            # experiment/workflow_a/jobs/workflow_a.yaml
            # experiment is just like runtime

        # saveto = f"{self.runtime_dir}/{self.name}.yaml"
            # saveto = Shell.map_filename(fr"~/.cloudmesh/workflow/{self.name}/runtime/{self.name}.yaml").path
            self.graph.save_to_yaml(filename)
        # else:
        #    saveto = filename
        self.graph.save_to_yaml(self.runtime_filename)

    def add_job(self,
                filename=None,
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
                venv=None,
                **kwargs
                ):
        """Add a job to the workflow.

        Args:
            name (str): name of job
            user (str): username for job
            host (str): where the job will be run
            label (str): what the node will say on the graph
            label_format: how the label will be formatted in the graph
            kind (str): the type of job, such as local, ssh, slurm
            status (str): how the job is doing, like ready, failed, done
            progress (int): a number from 0 to 100 that reports job
                completeness
            script (str): the script that the job will run
            exec (str): how the job will be executed
            pid (int or str): process id of the job
            **kwargs (kwargs): any other miscellaneous specifications
                for the job

        Returns:
            None: nothing
        """
        label = label or name
        user = user or Shell.user()
        host = host or Shell.host()
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
            venv=venv,
            instance=None
        )
        # update the times dat file to show created
        job_created_time = datetime.now().strftime(
            "%m/%d/%Y, %H:%M:%S")
        times_dict = None
        try:
            times_dict = yaml.safe_load(
                Path(self.times_filename).read_text())
        except:
            pass
        if times_dict is None:
            times_dict = {}
        if 'times' in times_dict:
            if f'created_time_{name}' not in times_dict['times']:
                times_dict['times'][
                    f'created_time_{name}'] = job_created_time
                d = str(yaml.dump(times_dict, indent=2))
                writefile(self.times_filename, d)
        else:
            times_dict.setdefault('times', {})[
                f'created_time_{name}'] = job_created_time
            d = str(yaml.dump(times_dict, indent=2))
            writefile(self.times_filename, d)
        self.save(filename=filename)

    def add_dependency(self, source, destination):
        """Add a job dependency to the workflow (and the graph).

        Args:
            source (str): job to be completed first
            destination (str): job to be completed after the source

        Returns:
            None: nothing
        """
        self.graph.add_dependency(source, destination)

    def add_dependencies(self, dependency):
        """Add a job dependency to the workflow (and the graph).

        Args:
            dependency (str): the dependency to be added

        Returns:
            None: nothing
        """
        self.graph.add_dependencies(dependency=dependency)

    def update_status(self, name, status):
        """Manually update a job's status.

        Args:
            name (str): the job whose status will be updated
            status (str): the new status to be set for the job

        Returns:
            None: nothing
        """
        self.graph[name]["status"] = status

    def set_progress(self, name, percent):
        """Manually update a job's progress.

        Args:
            name (str): name of the job
            percent (int): value from 0 to 100 for the progress

        Returns:
            None: nothing
        """
        self.graph[name]["progress"] = percent

    def update_progress(self, name):
        """Manually update the progress of a job according to its log file.

        Args:
            name (str): name of job

        Returns:
            None: nothing
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
        """Run a workflow in a parallel fashion.

        Args:
            directory (str): where the workflow should be run
            order: how the jobs should be run chronologically
            dryrun (bool): if true then the workflow isn't really run.
                for testing
            show (bool): whether to show graph as workflow is run
            period (float): how long to wait after showing the graph
            filename (str): where to save the graph

        Returns:
            None: nothing
        """
        finished = False

        undefined = []
        completed = []  # list of completed nodes
        running = []  # list of running nodes
        outstanding = list(self.jobs)  # list of outstanding nodes
        failed = []  # list of failed nodes

        def info():
            """Give information about the jobs of the workflow.

            Returns:
                None: nothing
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
            """Update the jobs status and progress.

            Args:
                name (str): name of job

            Returns:
                None: nothing
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
            """Run the job.

            Args:
                name (str): name of job

            Returns:
                None: nothing
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
                    # if os_is_windows():
                    #     win = gw.getWindowsWithTitle('MINGW64:')
                    #     win.activate()

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
        """Run the workflow in a topological fashion.

        Args:
            order: how the jobs should be run chronologically
            dryrun (bool): if true then the workflow isn't really run.
                for testing
            show (bool): whether to show the graph as workflow is run
            filename (str): where the graph should be saved

        Returns:
            None: nothing
        """

        experiment_dir = Path(Shell.map_filename(f'~/experiment').path).as_posix()
        Shell.rmdir(experiment_dir)
        graph_file = Path(Shell.map_filename(f'./runtime/{self.name}.svg').path).as_posix()

        def save_graph_to_file():
            for name in self.graph.nodes:
                msg = self.graph.create_label(name)
                self.graph.nodes[name]["label"] = msg
            self.graph.save(filename=graph_file,
                            colors="status",
                            layout=nx.circular_layout,
                            engine="dot")
        def display_in_browser():
            if not os.path.isfile(graph_file):
                return None
            if os_is_mac():
                Shell.open(filename=graph_file)
            elif os_is_linux():
                #  elif first and os_is_linux():
                # Shell.open(filename=filename)  # does not work
                os.system(f"chromium {graph_file}&")
                # os.system(f"eog {filename}")

            else:
                Shell.browser(graph_file)

        # bug the tno file needs to be better handled
        if order is None:
            order = self.sequential_order

        filename = filename or path_expand(f"runtime/{self.name}.svg")

        for i, name in enumerate(order()):
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
                venv = job['venv']
                _job = Job(name=name,
                           host=host,
                           username=username,
                           label=label,
                           label_format=label_format,
                           venv=venv,
                           workflow_name=self.name)
                _job.sync()
                _job.run()

                #add time beginning of workflow if not in times dat file
                workflow_started_time = datetime.now().strftime(
                    "%m/%d/%Y, %H:%M:%S")
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    times_dict = {}
                if 'times' in times_dict:
                    if f't0_{self.name}' not in times_dict['times']:
                        times_dict['times'][
                            f't0_{self.name}'] = workflow_started_time
                        d = str(yaml.dump(times_dict, indent=2))
                        writefile(self.times_filename, d)
                else:
                    times_dict.setdefault('times', {})[
                        f't0_{self.name}'] = workflow_started_time
                    d = str(yaml.dump(times_dict, indent=2))
                    writefile(self.times_filename, d)

                # update the times dat file if the job just started
                job_started_time = datetime.now().strftime(
                    "%m/%d/%Y, %H:%M:%S")
                times_dict = yaml.safe_load(
                    Path(self.times_filename).read_text())
                if times_dict is None:
                    times_dict = {}
                if 'times' in times_dict:
                    if f'tstart_{name}' not in times_dict['times']:
                        times_dict['times'][
                            f'tstart_{name}'] = job_started_time
                        d = str(yaml.dump(times_dict, indent=2))
                        writefile(self.times_filename, d)
                else:
                    times_dict.setdefault('times', {})[
                        f'tstart_{name}'] = job_started_time
                    d = str(yaml.dump(times_dict, indent=2))
                    writefile(self.times_filename, d)

                wait_interval = 0.5
                finished = False

                # this is to check if status has changed
                placeholder_progress = None
                placeholder_status = None

                while not finished:
                    status = _job.get_status()
                    progress = int(_job.get_progress(refresh=True))
                    print(f"Progress {_job.name}:", progress)
                    log = _job.get_log()
                    print(log)
                    finished = progress == 100
                    if progress == 100:
                        status = "done"
                    elif (progress > 0) and (progress < 100):
                        status = "running"

                    self.jobs[name]['status'] = status
                    self.jobs[name]['progress'] = progress
                    self.graph.save_to_yaml(filename=self.runtime_filename)
                    if (progress != placeholder_progress) or (status != placeholder_status):
                        # update the times dat file to show modified
                        job_modified_time = datetime.now().strftime(
                            "%m/%d/%Y, %H:%M:%S")
                        times_dict = yaml.safe_load(
                            Path(self.times_filename).read_text())
                        if times_dict is None:
                            times_dict = {}
                        if 'times' in times_dict:
                            times_dict['times'][
                                f'modified_time_{name}'] = job_modified_time
                            d = str(yaml.dump(times_dict, indent=2))
                            writefile(self.times_filename, d)
                        else:
                            times_dict.setdefault('times', {})[
                                f'modified_time_{name}'] = job_modified_time
                            d = str(yaml.dump(times_dict, indent=2))
                            writefile(self.times_filename, d)

                        # show end time if job just ended
                        if (progress == 100) and (status == 'done'):
                            job_end_time = workflow_end_time = datetime.now().strftime(
                                "%m/%d/%Y, %H:%M:%S")
                            times_dict = yaml.safe_load(
                                Path(self.times_filename).read_text())
                            if times_dict is None:
                                times_dict = {}
                            if 'times' in times_dict:
                                if f'tend_{name}' not in times_dict['times']:
                                    times_dict['times'][
                                        f'tend_{name}'] = job_end_time

                                # if this is the last job and it just finished
                                if i == len(order()) - 1:
                                    if f't1_{self.name}' not in times_dict[
                                            'times']:
                                        times_dict['times'][
                                            f't1_{self.name}'] = workflow_end_time
                            else:
                                times_dict.setdefault('times', {})[
                                    f'tend_{name}'] = job_end_time
                                if i == len(order()) - 1:
                                    times_dict.setdefault('times', {})[
                                        f't1_{self.name}'] = workflow_end_time
                            d = str(yaml.dump(times_dict, indent=2))
                            writefile(self.times_filename, d)

                        save_graph_to_file()
                        if show:
                            display_in_browser()
                        placeholder_status = status
                        placeholder_progress = progress

                    if not finished:
                        time.sleep(wait_interval)



                # if local or wsl or slurm:
                #     _job.watch(period=0.5)
                # elif ssh or slurm:
                #     _job.watch(period=3)

                self.graph.done(name)
                #print(self.table)
                #_job.watch(period=1)


                #print('Status: ', status)
                #print('Progress: ', progress)
                 # elif job['kind'] in ["local-slurm"]:
                #     raise NotImplementedError
                # elif job['kind'] in ["remote-slurm"]:
                #     raise NotImplementedError
            else:
                # banner(f"Job: {name}")
                Console.msg(f"running {name}")

    def display(self, filename=None, name='workflow', first=True):
        """Show the graph of the workflow.

        Args:
            filename (str): location of the graph
            name (str): name of the workflow to be displayed
            first (bool): if True then this is first time graph is
                displayed

        Returns:
            None: nothing
        """
        filename = filename or f"./{name}.svg"
        self.graph.save(filename=filename, colors="status", engine="dot")
        if os_is_mac():
            Shell.open(filename=filename)
        elif os_is_linux():
            #  elif first and os_is_linux():
            # Shell.open(filename=filename)  # does not work
            os.system(f"chromium {filename}&")
            # os.system(f"eog {filename}")

        else:
            Shell.browser(filename)

    def create_topological_order(self): #create_sequential_order
        # or put it in workflow or in both # mey need to be in workflow.
        """Update the graph while each node bget a number determined from get_sequential_order.

        Returns:
            list: list depicting the workflow
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
        #     node[top[i]]["number"] = i
        # pass

        numbers = []

        for job_to_be_indexed in self.sequential_order():
            numbers.append(self.sequential_order().index(
                job_to_be_indexed))

        jobs_and_id = list(zip(self.sequential_order(), numbers))

        for job_name, primary_key in zip(list(self.graph.nodes.keys()),
                                         jobs_and_id):
            current_job = primary_key[0]
            self.graph.nodes[current_job]['number'] = primary_key[1]

    def sequential_order(self): #get_sequentil_order
        """Return a list of the topological order of the workflow.

        Returns:
            list: list depicting the workflow
        """
        tuples = []
        for name, edge in self.graph.edges.items():
            tuples.append((edge["source"], edge["destination"]))
        g = nx.DiGraph(tuples)
        order = list(nx.topological_sort(g))
        return order

    @property
    def yaml(self):
        """Return a yaml dump of the nodes and dependencies of the workflow.

        Returns:
            str: yaml dump of workflow as string
        """
        data = {
            'nodes': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return yaml.dump(data)

    @property
    def dict_of_workflow(self):
        """Return a dict of the nodes and dependencies of the workflow.

        Returns:
            dict: dict of workflow
        """
        data = {
            'nodes': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return data

    def json(self, filepath=None):
        """Return the workflow as json string.

        Args:
            filepath (str): where the file is located

        Returns:
            str: a json string of the workflow
        """
        data = {
            'nodes': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return json.dumps(data, indent=2)

    @property
    def table(self):
        """Return a table of the workflow.

        Returns:
            None or PrettyTable or str or dict: a table of the workflow
        """
        # gvl rewritten
        with_label = True

        data = dict(self.graph.nodes)

        for name in self.graph.nodes:
            msg = self.graph.create_label(name)
            data[name]["label"] = msg

        if with_label:
            order = ['number',
                     'host',
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
            order = ['number',
                     'host',
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
        """Return a table of the workflow.

        Args:
            with_label (bool): whether to include label in table

        Returns:
            None or PrettyTable or str or dict: a table of the workflow
        """
        # gvl rewritten
        # with_label = False

        data = dict(self.graph.nodes)

        for name in self.graph.nodes:
            label = self.graph.nodes[name]["label"]
            msg = self.graph.create_label(name)
            data[name]["label"] = msg

        if with_label:
            order = ['number',
                     'host',
                     'status',
                     'label',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']
        else:
            order = ['number',
                     'host',
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
        """Delete workflow from the local file system.

        Returns:
            None: nothing
        """
        # gvl rewritten
        # TODO: the rm seems wrong
        d = os.path.dirname(self.filename)
        os.system(f"rm -r {d}")
        self.graph = None
        self.jobs = None
        self.graph.edges = None

    def remove_job(self, name, state=False):
        """Remove a particular job from the workflow.

        Args:
            name (str): name of job to be removed from workflow
            state (bool): whether to save workflow with state after job
                removal

        Returns:
            None: nothing
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
        # if self.graph.nodes[name]["parent"]:
        #     dellist.append(self.graph.nodes[name]["parent"])
        for key in dellist:
            self.graph.edges.pop(key)

        if state:
            self.save_with_state(self.filename)
        else:
            self.save(self.filename)

    def status(self):
        """Return details of the workflow in dict format.

        Returns:
            dict: details of workflow in dict format
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

    def analyze_states(self):
        """Return a wordcount on status.

        Returns:
            dict: dict of occurrences of each status
        """
        states = []
        for state in ['completed', 'ready', 'failed', 'submitted', 'running']:
            states.append(state)
        for name in self.jobs:
            states.append(self.jobs[name]["status"])

        from collections import Counter
        count = Counter(states)
        for state in ['completed', 'ready', 'failed', 'submitted', 'running']:
            count[state] = count[state] - 1
        return count
