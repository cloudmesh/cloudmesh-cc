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
import json
from cloudmesh.cc.labelmaker import Labelmaker

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
        self.sep = "-"
        self.edges = dotdict()
        self.nodes = dotdict()
        self.colors = None
        self.set_status_colors()
        self.name = name
        self.filename = filename

        if filename is not None and not clear:
            self.load(filename=filename)
        #
        # maybe
        # config:
        #    name:
        #    colors:

    def clear(self):
        self.sep = "-"
        self.edges = dotdict()
        self.nodes = dotdict()
        self.colors = None
        self.set_status_colors()
        self.name = None
        self.filename = None

    def __getitem__(self, name):
        return self.nodes[name]

    def set_status_colors(self):
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
        if self.colors is None:
            self.colors = {}
        if key not in self.colors:
            self.colors[key] = {}
        self.colors[key].update(**colors)


    def __str__(self):
        data = {
            "nodes": dict(self.nodes),
            "dependencies": dict(self.edges),
        }
        workflow = {'workflow': data}

        if self.colors is not None:
            workflow["colors"] = dict(self.colors)

        return yaml.dump(workflow, indent=2)

    def load(self, filename=None):
        # if filename is not None:
        #    raise NotImplementedError
        # should read from file the graph, but as we do Queues yaml dic
        # we do not need filename read right now

        try:
            self.name = os.path.basename(filename).split(".")[0]
        except:
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
        if "parent" not in self.nodes[destination]:
            self.nodes[destination]["parent"] = []
        if "parent" not in self.nodes[source]:
            self.nodes[source]["parent"] = []
        self.nodes[destination]["parent"].append(source)

    def done(self, parent):
        """
        removes from all nodes the names parent

        Args:
            parent ():

        Returns:

        """
        for name in self.nodes:
            if "parent" in self.nodes[name]:
                if parent in self.nodes[name]["parent"]:
                    self.nodes[name]["parent"].remove(parent)

    def todo(self):
        """
        finds all nodes with no parents and progress != 100

        Returns: list of node names with no parents

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
        self.nodes[name]["status"] = status

    def get_status(self, name):
        return self.nodes[name]["status"]

    def add_dependency(self, source, destination):
        self.add_dependencies(self, f"{source},{destination}")

    def add_dependencies(self, dependency, nodedata=None, edgedata=None):
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

    def save(self,
             filename="test.svg",
             colors=None,
             layout=nx.spring_layout,
             engine="networkx"):
        dot = graphviz.Digraph(comment='Dot Graph')
        dot.attr('node', shape="rounded")
        graph = nx.DiGraph()

        color_map = []
        for name, e in self.nodes.items():
            if colors is None:
                graph.add_node(name)
                label = self.nodes[name]["label"]
                replacement = Labelmaker(label)
                msg = replacement.get(**self.nodes[name])
                dot.node(name, color='white', label=msg)
                color_map.append('white')
            else:
                value = e[colors]
                color_map.append(self.colors[colors][value])
                if name in ["start", "end"]:
                    shape = "diamond"
                else:
                    shape = "rounded"
                try:
                    label = self.nodes[name]["label"]
                except:
                    label = name
                replacement = Labelmaker(label)
                msg = replacement.get(**self.nodes[name])
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

    def __init__(self, name=None, filename=None, user=None, host=None, load=True):
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
            self,name = 'workflow'

        # self.filename = filename or f"~/.cloudmesh/workflow/{self.name}/{self.name}.yaml"
        if not filename:
            self.filename = f"~/.cloudmesh/workflow/{self.name}/{self.name}.yaml"
        else:
            self.filename = filename
        self.filename = path_expand(self.filename)
        Shell.mkdir(os.path.dirname(self.filename))


        try:
            self.name = os.path.basename(filename).split(".")[0]
        except:
            self.name = "workflow"





        self.user = user
        self.host = host

        try:
            print("Workflow Filename:", self.filename)
            self.graph = Graph(name=name, filename=filename)
            # gvl addded load but not tested
            if load:
                self.load(self.filename)
        except Exception as e:  # noqa: E722
            Console.error(e, traceflag=True)
            pass

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
        return str(self.graph)

    @property
    def jobs(self):
        return self.graph.nodes  # [name]

    def __getitem__(self, name):
        return self.jobs[name]

    def job(self, name):
        return self.jobs[name]

    @property
    def dependencies(self):
        # gvl implemented but not tested
        return self.graph.edges  # [name]

    def predecessor(self, name):
        # GVL reimplemented but not tested
        predecessors = []
        edges = self.dependencies

        for _name, edge in edges.items():
            if edge["destination"] == name:
                predecessors.append(edge["source"])
        return predecessors

    def get_predecessors(self, name):
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

    def save_with_state(self, filename, stdout=False):
        print(self.graph)
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
                print ("NNNN", node)
                if "script" not in node:
                    node["script"] = f"{name}.sh"
                pprint (node)
                job = Job.create(filename=node['script'], exec=node["exec"])
                print (job)

    def save(self, filename):
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
                kind="local",
                status="ready",
                progress=0,
                script=None,
                exec=None,
                pid=None,
                **kwargs
                ):

        label = label or name
        user = user or self.user or Shell.user()
        host = host or self.host or Shell.host()

        if script is None:
            script = f"{name}.sh"

        now = str(DateTime.now())
        self.graph.add_node(
            name=name,
            label=label,
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
        self.graph.add_dependency(source, destination)

    def add_dependencies(self, dependency):
        self.graph.add_dependencies(dependency=dependency)

    def update_status(self, name, status):
        self.graph[name]["status"] = status

    def set_progress(self, name, percent):
        self.graph[name]["progress"] = percent

    def update_progress(self, name):
        # fetches log file and looks for progress event TBD
        # once progress is fetched set it for the named job
        raise NotImplementedError

    def run_parallel(self,
                     directory="~/experiment",
                     order=None,
                     parallel=False,
                     dryrun=False,
                     show=True,
                     period=0.5,
                     filename=None):
        finished = False

        undefined = []
        completed = []  # list of completed nodes
        running = []  # list of runiing nodes
        outstanding = list(self.jobs)  # list of outstanding nodes
        failed = []  # list of failed nodes

        def info():
            print("Undefined:   ", undefined)
            print("Completed:   ", completed)
            print("Running:     ", running)
            print("Outstanding: ", outstanding)
            print("Failed:      ", failed)
            print()
            print("Todo:       ", self.graph.todo())
            print("Dependencies:", len(self.graph.edges))

        def update(name):
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
                    print(str(job["instance"]))
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
                self.graph.save(filename=filename,
                                colors="status",
                                engine="dot")
                if first and os_is_mac():
                    os.system(f'open {filename}')
                    first = False
                elif first and os_is_linux():
                    os.system(f'gopen {filename}')
                else:
                    cwd = os.getcwd()
                    os.system(f'start chrome {cwd}\\{filename}')
            time.sleep(period)
            finished = len(completed) == len(self.jobs)

            # debugging
            #info()
            #input()

        # save graph occurs again to make sure things are being saved
        self.graph.save(filename=filename,
                        colors="status",
                        engine="dot")

    def run_topo(self, order=None, parallel=False, dryrun=False, show=True, filename=None):
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
                host = job['host']
                username = job['user']
                label = name
                _job = Job(name=name,
                          host=host,
                          username=username,
                          label=label)
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
                banner(name)
                print(str(job))
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
                self.graph.save(filename=filename, colors="status",
                                layout=nx.circular_layout, engine="dot")
                if first and os_is_mac():
                    os.system(f'open {filename}')
                    first = False
                elif first and os_is_linux():
                    os.system(f'gopen {filename}')
                else:
                    cwd = os.getcwd()
                    os.system(f'start chrome {cwd}\\{filename}')

    def display(self, filename=None, name='workflow', first=True):
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

    def sequential_order(self):
        tuples = []
        for name, edge in self.graph.edges.items():
            tuples.append((edge["source"], edge["destination"]))
        g = nx.DiGraph(tuples)
        order = list(nx.topological_sort(g))
        return order

    @property
    def yaml(self):
        data = {
            'nodes: ': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return yaml.dump(data)

    def json(self, filepath=None):
        data = {
            'nodes: ': dict(self.jobs),
            'dependencies': dict(self.dependencies)
        }
        return json.dumps(data, indent=2)

    @property
    def table(self):
        # gvl rewritten
        with_label = False

        data = dict(self.graph.nodes)

        for name in self.graph.nodes:
            label = self.graph.nodes[name]["label"]
            replacement = Labelmaker(label)
            msg = replacement.get(**self.graph.nodes[name])
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

    def table2(self, with_label=False):
        # gvl rewritten
        # with_label = False

        data = dict(self.graph.nodes)

        for name in self.graph.nodes:
            label = self.graph.nodes[name]["label"]
            replacement = Labelmaker(label)
            msg = replacement.get(**self.graph.nodes[name])
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
        # gvl rrewritten
        # TODO: the rm seems wrong
        d = os.path.dirname(self.filename)
        os.system("rm -r {d}")
        self.graph = None
        self.jobs = None
        self.graph.edges = None

    def remove_job(self, name, state=False):
        # remove job

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
        # gvl implemented but not tested
        s = "done"
        _status = {"workflow": s,
                   "job": None}
        for name in self.jobs:
            state = self.jobs["status"]
            progress = self.jobs["progress"]
            _status["job"][name] = {
                "status": state,
                "progress": progress
            }
            if state in ["running"]:
                s = "running"
            elif state in ["undefined"]:
                s = "undefined"
            elif state in ["filed"]:
                s = "failed"
        _status["workflow"] = s
        return _status
