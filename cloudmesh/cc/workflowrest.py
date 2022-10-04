"""Cloudmesh cc REST workflow."""
import requests


class RESTWorkflow:

    def __init__(self):
        self.address = "http://127.0.0.1:8000"

    # @app.get("/workflows")
    def list_workflows(self):
        """
        This command returns a list of workflows that is found within the server.

        You can invoke this function also with a curl command:

        curl -X 'GET' 'http://127.0.0.1:8000/workflows' -H 'accept: application/json'

        :return: list of workflow names
        :rtype: dict
        """
        content = requests.get(f"{self.address}/workflows") # return as json string
        return content  # likely a dict

    def add_job(self, workflow_name: str, **kwargs):
        """
        This command adds a job to a workflow that is specified in the
        provided workflow_name string.

        :return: all jobs within workflow
        :rtype: dict
        """
        jobname = kwargs['jobname']
        user = kwargs['user']
        host = kwargs['host']
        kind = kwargs['kind']
        url = f'''http://127.0.0.1:8000/workflow/job/{workflow_name}?job={jobname}&user={user}&host={host}&kind={kind}'''
        if 'status' in kwargs:
            status = kwargs['status']
        else:
            status = 'undefined'
        url += f'&status={status}'
        if 'script' in kwargs:
            script = kwargs['script']
            url += f'&script={script}'
        elif 'exec' in kwargs:
            exec = kwargs['exec']
            url += f'&exec={exec}'
        if 'progress' in kwargs:
            progress = kwargs['progress']
            url += f'&progress={progress}'
        if 'label' in kwargs:
            label = kwargs['label']
            url += f'&label={label}'
        my_dict = {
            "name": jobname,
            "user": user,
            "host": host,
            "kind": kind,
            "status": status,
            "script": script
        }
        print(url)

        # curl -X 'POST' 'http://127.0.0.1:8000/workflow/workflow?job=c&user=gregor&host=localhost&kind=local&status=ready&script=c.sh' -H 'accept: application/json'/
        # try:
        #     r = os.system(f'''curl -X 'POST' {url} -H 'accept: application/json'/''')
        # except Exception as e:
        #     print(e.output)
        content = requests.get(url)
        return content

    def upload_workflow(self, directory: str = None, archive: str = None, yaml: str = None):
        """

        :return:
        """
        url = 'http://127.0.0.1:8000/workflow/upload'
        if directory:
            url += f'?directory={directory}'
        if archive:
            url += f'?archive={directory}'
        if yaml:
            url += f'?yaml={directory}'

        #files = {'file': open(file_path, 'rb')}

        r = requests.post(url)
        return r


    def get_workflow(self, workflow_name: str, job_name: str=None):
        """

        :param workflow_name:
        :return:
        """
        url = f'http://127.0.0.1:8000/workflow/{workflow_name}'
        if job_name:
            url += f'?job={job_name}'
        r = requests.get(url)
        return r

    def run_workflow(self, workflow_name: str, run_type: str='topo'):
        """

        :return:
        """
        url = f'http://127.0.0.1:8000/workflow/run/{workflow_name}?type={run_type}'
        r = requests.get(url)
        return r

    def delete_workflow(self, workflow_name: str, job_name: str=None):
        url = f'http://127.0.0.1:8000/workflow/{workflow_name}'
        if job_name:
            url += f'?job={job_name}'
        r = requests.delete(url)
        return r


'''
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
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError
        #return str(self.graph)

    @property
    def jobs(self):
        raise NotImplementedError
        # return self.graph.nodes  # [name]

    def __getitem__(self, name):
        raise NotImplementedError
        # return self.jobs[name]

    def job(self, name):
        raise NotImplementedError
        # return self.jobs[name]

    @property
    def dependencies(self):
        raise NotImplementedError
        #
        # gvl implemented but not tested
        # return self.graph.edges  # [name]

    def predecessor(self, name):
        raise NotImplementedError
        #
        # GVL reimplemented but not tested
        # predecessors = []
        # edges = self.dependencies
        #
        # for _name, edge in edges.items():
        #     if edge["destination"] == name:
        #         predecessors.append(edge["source"])
        # return predecessors

    def get_predecessors(self, name):
        raise NotImplementedError
        # """
        # figure out all of the dependencies of the name node
        # then test if each node in front (parent) has progress of 100
        # if the parent has progress 100, remove those nodes
        # :return:
        # """
        # parents = []
        # candidates = self.predecessors(name)
        # print(candidates)
        # for candidate in candidates:
        #     if candidate['progress'] != 100:
        #         parents.append(candidate)
        #
        # if parents == []:
        #     return None
        # else:
        #     return parents

    def save_with_state(self, filename, stdout=False):
        raise NotImplementedError
        # print(self.graph)
        # data = {}
        # data['workflow'] = {
        #     "nodes": dict(self.graph.nodes),
        #     "dependencies": dict(self.graph.edges),
        # }
        # if self.graph.colors:
        #     data["colors"] = dict(self.graph.colors)
        #
        # d = str(yaml.dump(data, indent=2))
        # writefile(filename, d)
        # if stdout:
        #     return d

    def load_with_state(self, filename):
        raise NotImplementedError
        # s = readfile(filename)
        # data = yaml.safe_load(s)
        # if "nodes" in data['workflow']:
        #     self.graph.nodes = data['workflow']['nodes']
        # if "dependencies" in data['workflow']:
        #     self.graph.edges = data['workflow']['dependencies']
        # if "colors" in data:
        #     self.graph.colors = data['colors']

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
        raise NotImplementedError
        # self.graph = Graph()
        # # if not clear:
        # self.graph.load(filename=filename)
        #
        # # with open(filename, 'r') as stream:
        # #     graph = yaml.safe_load(stream)
        # #
        # # dependencies = graph["workflow"]
        # #nodes = graph["workflow"]["nodes"].items()
        # #
        # # # for name, node in graph["workflow"]["nodes"].items():
        # for name, node in self.graph.nodes.items():
        #      if "name" not in node:
        #          node["name"] = name
        #      self.add_job(**node)
        # #
        # # for edge in dependencies:
        # #     self.add_dependencies(edge)
        #
        #
        # # expand script and exec and save shell scripts
        # for name, node in self.graph.nodes.items():
        #     if node['exec'] is None and node['script'] is not None:
        #         del node['exec']
        #     if "exec" in node and node["kind"] == "local":
        #         from cloudmesh.cc.job.localhost.Job import Job
        #         print ("NNNN", node)
        #         if "script" not in node:
        #             node["script"] = f"{name}.sh"
        #         pprint (node)
        #         job = Job.create(filename=node['script'], exec=node["exec"])
        #         print (job)

    def save(self, filename):
        rasie NotImplementedError
        # if os_is_windows():
        #     name = os.path.basename(filename).replace(r".yaml", "")
        #     dir = Shell.map_filename(fr"~/.cloudmesh/workflow/{name}/{name}.yaml").path
        #     self.graph.save_to_file(dir)
        # self.graph.save_to_file(filename)

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
        raise NotImplementedError
        #
        # label = label or name
        # user = user or self.user or Shell.user()
        # host = host or self.host or Shell.host()
        #
        # if script is None:
        #     script = f"{name}.sh"
        #
        # now = str(DateTime.now())
        # self.graph.add_node(
        #     name=name,
        #     label=label,
        #     kind=kind,
        #     user=user,
        #     host=host,
        #     status=status,
        #     progress=progress,
        #     created=now,
        #     modified=now,
        #     script=script,
        #     exec=exec,
        #     instance=None
        # )
        # self.save(self.filename)



    def add_dependency(self, source, destination):
        raise NotImplementedError
        #    self.graph.add_dependency(source, destination)

    def add_dependencies(self, dependency):
        raise NotImplementedError
        # self.graph.add_dependencies(dependency=dependency)

    def update_status(self, name, status):
        raise NotImplementedError #
        # self.graph[name]["status"] = status

    def set_progress(self, name, percent):
        raise NotImplementedError #
        # self.graph[name]["progress"] = percent

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
        raise NotImplementedError
        #
        # finished = False
        #
        # undefined = []
        # completed = []  # list of completed nodes
        # running = []  # list of runiing nodes
        # outstanding = list(self.jobs)  # list of outstanding nodes
        # failed = []  # list of failed nodes
        #
        # def info():
        #     print("Undefined:   ", undefined)
        #     print("Completed:   ", completed)
        #     print("Running:     ", running)
        #     print("Outstanding: ", outstanding)
        #     print("Failed:      ", failed)
        #     print()
        #     print("Todo:       ", self.graph.todo())
        #     print("Dependencies:", len(self.graph.edges))
        #
        # def update(name):
        #     banner(f"update {name}")
        #     log = self.jobs[name]["instance"].get_log()
        #     status = self.jobs[name]["instance"].get_status()
        #     progress = self.jobs[name]["instance"].get_progress()
        #     self.jobs[name]['status'] = status
        #     self.jobs[name]['progress'] = progress
        #
        #     # print("Job data", name, status, progress)
        #
        #
        #     if progress == 100:
        #         self.graph.done(name)
        #         if name in running:
        #             running.remove(name)
        #         if name not in completed:
        #             completed.append(name)
        #         if name in undefined:
        #             undefined.remove(name)
        #
        #     elif status == "undefined":
        #         if name in running:
        #             running.remove(name)
        #         if name not in completed:
        #             completed.append(name)
        #         if name not in undefined and name not in outstanding:
        #             undefined.append(name)
        #     # elif status == 'running':
        #     #    ready.remove(name)
        #



        def start(name):
            raise NotImplementedError
        #
        #     banner(name)
        #
        #     job = self.job(name=name)
        #     wf_name = os.path.basename(filename).split(".")[0]
        #     experiment_directory = f'~/experiment/{wf_name}/{name}'
        #     job['directory'] = experiment_directory
        #     if not dryrun and job["status"] in ["ready"]:
        #         local = wsl = ssh = slurm = lsf = False
        #         if job['kind'] in ["local"]:
        #             local = True
        #             from cloudmesh.cc.job.localhost.Job import Job
        #         elif job['kind'] in ["wsl"]:
        #             wsl = True
        #             from cloudmesh.cc.job.wsl.Job import Job
        #         elif job['kind'] in ['ssh']:
        #             ssh = True
        #             from cloudmesh.cc.job.ssh.Job import Job
        #         elif job['kind'] in ['slurm']:
        #             slurm = True
        #             from cloudmesh.cc.job.slurm.Job import Job
        #         elif job['kind'] in ['lsf']:
        #             lsf = True
        #             from cloudmesh.cc.job.lsf.Job import Job
        #         else:
        #             from cloudmesh.cc.job.localhost.Job import Job
        #         job["status"] = "running"
        #         name = job['name']
        #         host = job['host']
        #         username = job['user']
        #         label = name
        #         if local or wsl:
        #             job["instance"] = Job(name=name,
        #                                   host=host,
        #                                   username=username,
        #                                   label=label,
        #                                   directory=experiment_directory)
        #         if ssh or slurm:
        #             job = Job(name=name,
        #                       host=host,
        #                       username=username,
        #                       label=label,
        #                       directory=experiment_directory)
        #             job.sync()
        #             job.run()
        #         if local or wsl:
        #             job["instance"].sync()
        #             job["instance"].run()
        #             print(str(job["instance"]))
        #             running.append(name)
        #             outstanding.remove(name)
        #
        #         # elif job['kind'] in ["local-slurm"]:
        #         #     raise NotImplementedError
        #         # elif job['kind'] in ["remote-slurm"]:
        #         #     raise NotImplementedError
        #     else:
        #         # banner(f"Job: {name}")
        #         Console.msg(f"running {name}")
        #
        # if os_is_windows():
        #     Shell.mkdir("./tmp")
        #     filename = filename or "tmp/workflow.svg"
        # else:
        #     filename = filename or "/tmp/workflow.svg"
        #
        # first = True
        #
        # while not finished:
        #
        #     info()
        #
        #     for name in running:
        #         update(name)
        #
        #     todo = self.graph.todo()
        #
        #     for name in todo:
        #         print("TODO", name)
        #         start(name)
        #
        #     # print(self.table)
        #     print(self.table2(with_label=True))
        #
        #     if show:
        #         self.graph.save(filename=filename, colors="status", engine="dot")
        #         if first and os_is_mac():
        #             Shell.open(filename=filename)
        #             first = False
        #         elif first and os_is_linux():
        #             Shell.open(filename=filename)
        #         else:
        #             Shell.browser(filename)
        #     time.sleep(period)
        #     finished = len(completed) == len(self.jobs)
        #
        #     # debugging
        #     #info()
        #     #input()
        #
        # # save graph occurs again to make sure things are being saved
        # self.graph.save(filename=filename,
        #                 colors="status",
        #                 engine="dot")

    def run_topo(self, order=None, parallel=False, dryrun=False, show=True, filename=None):
        raise NotImplementedError
        # # bug the tno file needs to be better handled
        # if order is None:
        #     order = self.sequential_order
        #
        # if os_is_windows() and filename is None:
        #     Shell.mkdir("./tmp")
        #     filename = filename or f"tmp/{self.name}.svg"
        # else:
        #     filename = filename or f"/tmp/{self.name}.svg"
        #
        # first = True
        # for name in order():
        #     job = self.job(name=name)
        #
        #     if not dryrun:
        #         local = wsl = ssh = slurm = lsf = False
        #         if job['kind'] in ["local"]:
        #             local = True
        #             from cloudmesh.cc.job.localhost.Job import Job
        #         elif job['kind'] in ["wsl"]:
        #             wsl = True
        #             from cloudmesh.cc.job.wsl.Job import Job
        #         elif job['kind'] in ['ssh']:
        #             ssh = True
        #             from cloudmesh.cc.job.ssh.Job import Job
        #         elif job['kind'] in ['slurm']:
        #             slurm = True
        #             from cloudmesh.cc.job.slurm.Job import Job
        #         elif job['kind'] in ['lsf']:
        #             lsf = True
        #             from cloudmesh.cc.job.lsf.Job import Job
        #         else:
        #             from cloudmesh.cc.job.localhost.Job import Job
        #         if local or ssh or slurm:
        #             job["status"] = "running"
        #         name = job['name']
        #         host = job['host']
        #         username = job['user']
        #         label = name
        #         _job = Job(name=name,
        #                   host=host,
        #                   username=username,
        #                   label=label)
        #         _job.sync()
        #         _job.run()
        #
        #         if local or wsl or slurm:
        #             _job.watch(period=0.5)
        #         elif ssh or slurm:
        #             _job.watch(period=3)
        #
        #         self.graph.done(name)
        #         print(self.table)
        #         _job.watch(period=1)
        #         log = _job.get_log()
        #         status = _job.get_status()
        #         progress = _job.get_progress()
        #         if progress == 100:
        #             status = "done"
        #         print('Status: ', status)
        #         print('Progress: ', progress)
        #         self.jobs[name]['status'] = status
        #         self.jobs[name]['progress'] = progress
        #
        #         # elif job['kind'] in ["local-slurm"]:
        #         #     raise NotImplementedError
        #         # elif job['kind'] in ["remote-slurm"]:
        #         #     raise NotImplementedError
        #     else:
        #         # banner(f"Job: {name}")
        #         Console.msg(f"running {name}")
        #
        #     if show:
        #         self.graph.save(filename=filename, colors="status",
        #                         layout=nx.circular_layout, engine="dot")
        #         if first and os_is_mac():
        #             Shell.open(filename=filename)
        #             first = False
        #         elif first and os_is_linux():
        #             Shell.open(filename=filename)
        #         else:
        #             Shell.browser(filename)

    def display(self, filename=None, name='workflow', first=True):
        raise NotImplementedError
    #     if os_is_windows():
    #         Shell.mkdir("./tmp")
    #         filename = filename or f"tmp/{name}.svg"
    #     else:
    #         filename = filename or f"/tmp/{name}.svg"
    #     self.graph.save(filename=filename, colors="status", engine="dot")
    #     if first and os_is_mac():
    #         os.system(f'open {filename}')
    #         first = False
    #     elif first and os_is_linux():
    #         os.system(f'gopen {filename}')
    #     else:
    #         cwd = os.getcwd()
    #         os.system(f'start chrome {cwd}\\{filename}')
    #
    # def sequential_order(self):
    #     tuples = []
    #     for name, edge in self.graph.edges.items():
    #         tuples.append((edge["source"], edge["destination"]))
    #     g = nx.DiGraph(tuples)
    #     order = list(nx.topological_sort(g))
    #     return order
    #
    # @property
    # def yaml(self):
    #     data = {
    #         'nodes: ': dict(self.jobs),
    #         'dependencies': dict(self.dependencies)
    #     }
    #     return yaml.dump(data)
    #
    # def json(self, filepath=None):
    #     data = {
    #         'nodes: ': dict(self.jobs),
    #         'dependencies': dict(self.dependencies)
    #     }
    #     return json.dumps(data, indent=2)
    #
    # @property
    # def table(self):
    #     # gvl rewritten
    #     with_label = False
    #
    #     data = dict(self.graph.nodes)
    #
    #     for name in self.graph.nodes:
    #         label = self.graph.nodes[name]["label"]
    #         replacement = Labelmaker(label)
    #         msg = replacement.get(**self.graph.nodes[name])
    #         data[name]["label"] = msg
    #
    #     if with_label:
    #         order = ['host',
    #                  'status',
    #                  'label',
    #                  'name',
    #                  'progress',
    #                  'script',
    #                  'user',
    #                  'parent',
    #                  'kind']
    #     else:
    #         order = ['host',
    #                  'status',
    #                  'name',
    #                  'progress',
    #                  'script',
    #                  'user',
    #                  'parent',
    #                  'kind']
    #
    #     return Printer.write(self.graph.nodes,
    #                          order=order)

    def table2(self, with_label=False):
        raise NotImplementedError
        # # gvl rewritten
        # # with_label = False
        #
        # data = dict(self.graph.nodes)
        #
        # for name in self.graph.nodes:
        #     label = self.graph.nodes[name]["label"]
        #     replacement = Labelmaker(label)
        #     msg = replacement.get(**self.graph.nodes[name])
        #     data[name]["label"] = msg
        #
        # if with_label:
        #     order = ['host',
        #              'status',
        #              'label',
        #              'name',
        #              'progress',
        #              'script',
        #              'user',
        #              'parent',
        #              'kind']
        # else:
        #     order = ['host',
        #              'status',
        #              'name',
        #              'progress',
        #              'script',
        #              'user',
        #              'parent',
        #              'kind']
        #
        # return Printer.write(self.graph.nodes,
        #                      order=order)



    def remove_workflow(self):
        raise NotImplementedError
        # # gvl rrewritten
        # # TODO: the rm seems wrong
        # d = os.path.dirname(self.filename)
        # os.system("rm -r {d}")
        # self.graph = None
        # self.jobs = None
        # self.graph.edges = None

    def remove_job(self, name, state=False):
        raise NotImplementedError
        # # remove job
        #
        # # del self.jobs[name]
        # p = self.jobs.pop(name)
        # # print("popped:",p)
        #
        # # remove dependencies to job
        # dependencies = self.graph.edges.items()
        #
        # dellist = []
        # for edge, dependency in dependencies:
        #     if dependency["source"] == name or dependency["destination"] == name:
        #         dellist.append(edge)
        #
        # # TODO: remove parent node
        # for key in dellist:
        #     self.graph.edges.pop(key)
        #
        # if state:
        #     self.save_with_state(self.filename)
        # else:
        #     self.save(self.filename)

    def status(self):
        raise NotImplementedError
        # # gvl implemented but not tested
        # s = "done"
        # _status = {"workflow": s,
        #            "job": None}
        # for name in self.jobs:
        #     state = self.jobs["status"]
        #     progress = self.jobs["progress"]
        #     _status["job"][name] = {
        #         "status": state,
        #         "progress": progress
        #     }
        #     if state in ["running"]:
        #         s = "running"
        #     elif state in ["undefined"]:
        #         s = "undefined"
        #     elif state in ["filed"]:
        #         s = "failed"
        # _status["workflow"] = s
        # return _status
'''
