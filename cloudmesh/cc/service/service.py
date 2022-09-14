import yaml
import logging
import threading
from typing import List
import networkx as nx
from pathlib import Path

from cloudmesh.cc.queue import Queues
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common import dotdict
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import File
from fastapi import UploadFile
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse
from pydantic import BaseModel

from cloudmesh.cc.__version__ import version as cm_version

from fastapi.staticfiles import StaticFiles
import pkg_resources
from cloudmesh.common.console import Console
import os
import io
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common.util import banner
import pandas as pd
import glob
import json

"""
all the URLs.
@app.get("/", tags=['workflow'])
@app.get("/workflows", tags=['workflow'])
    ?json
    ?yaml
    ?html
    ?dict
    
@app.post("/upload", tags=['workflow'])
@app.delete("/workflow/{name}", tags=['workflow'])
@app.get("/workflow/{name}", tags=['workflow'])
@app.get("/run/{name}", tags=['workflow'])
@app.post("/workflow/{name}", tags=['workflow'])
"""


def test_run():
    """
    creates a test queue with several different jobs
    :return: Queues object
    :rtype: Queues
    """
    kind = 'yamldb'
    q = Queues(filename='~/.cloudmesh/queue/queuetest1')
    q.create(name='local')
    q.create(name='rivanna')
    q.add(name='local', job='job01', command='pwd')
    q.add(name='local', job='job02', command='ls')
    q.add(name='local', job='job03', command='hostname')
    q.add(name='rivanna', job='job04', command='pwd')
    q.add(name='rivanna', job='job05', command='ls - a')
    q.add(name='rivanna', job='job06', command='hostname')
    q.add(name='rivanna', job='job07', command='git status')
    return q


def get_available_workflows():
    """
    returns workflow dirs found in .cloudmesh directory
    :return: names of workflows found
    :rtype: list
    """
    folders = []
    directory = path_expand(f"~/.cloudmesh/workflow/")
    result = glob.glob(f"{directory}/*")

    # result = [os.path.basename(e) for e in result]

    def check_if_workflow_has_yaml(folder):
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith('.yaml'):
                    return True

    for possible_folder in result:
        if check_if_workflow_has_yaml(possible_folder):
            folders.append(os.path.basename(possible_folder))

    return folders


def dict_of_available_workflows():
    """
    looks inside ~/.cloudmesh/workflow directory
    for available workflows and returns them
    as initialized workflows inside a dict
    :return: available workflows as dict
    :rtype: dict
    """
    list_of_workflows = []
    dict_of_workflow_dicts = {}
    folders = get_available_workflows()

    for workflow in folders:
        list_of_workflows.append(load_workflow(name=workflow))
    for workflow in list_of_workflows:
        dict_of_workflow_dicts[workflow.name] = workflow.dict_of_workflow
    return dict_of_workflow_dicts


class Jobpy(BaseModel):
    name: str
    user: str
    host: str
    label: str | None = None
    kind: str | None = None
    status: str | None = None
    progress: int | None = None
    script: str | None = None
    pid: int | None = None
    parent: str | None = None


q = test_run()

app = FastAPI(title="cloudmesh-cc", version=cm_version)

#
# REGISTER template and static dir
#

static_dir = pkg_resources.resource_filename("cloudmesh.cc", "service/static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

template_dir = pkg_resources.resource_filename("cloudmesh.cc", "service/templates")
templates = Jinja2Templates(directory=template_dir)

www_dir = pkg_resources.resource_filename("cloudmesh.cc", "www")
www = Jinja2Templates(directory=www_dir)


#
# ROUTES
#

# # deprecated only here as example/test once working example is implemented, remove
# @app.get("/item/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     global q
#     jobs = []
#     for queue in q.queues:
#         for job in q.queues[queue]:
#             jobs.append(q.queues[queue][job])
#     order = q.queues[queue][job].keys()
#     order = [word.capitalize() for word in order]
#     Console.error(str(order))
#
#     return templates.TemplateResponse("templates/item.html",
#                                       {"request": request,
#                                        "id": id,
#                                        "jobs": jobs,
#                                        "order": order})
#
# # deprecated only here as example/test once working example is implemented, remove
# @app.get("/items", response_class=HTMLResponse)
# async def item_table(request: Request):
#     return templates.TemplateResponse("templates/table.html",
#                                       {"request": request})

def load_workflow(name: str, load_with_graph=False) -> Workflow:
    """
    loads a workflow corresponding to given name
    :param name:
    :type name: str
    :return: loaded workflow
    :rtype: Workflow
    """
    filename = Shell.map_filename(f"~/.cloudmesh/workflow/{name}/{name}.yaml").path
    w = Workflow(filename=filename, load=True)
    # w.__init__(filename=filename)
    # w.load(filename=filename)
    if load_with_graph:
        pass
        # w.graph.save_to_file(filename=f"{name}.svg")
    # w.load(filename)
    # print(w.yaml)
    return w


#
# HOME
#

@app.get("/", tags=['workflow'])
@app.get("/home", tags=['workflow'])
async def home_page(request: Request):
    """
    home function that features html and
    sidebar
    :return: up message
    """
    os.path.dirname(__file__)
    os.chdir(os.path.dirname(__file__))
    os.chdir(Path('../../..').as_posix())
    folders = get_available_workflows()
    page = "cloudmesh/cc/service/markdown/home.md"
    import markdown
    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("home.html", {"request": request,
                                                    "workflowlist": folders,
                                                    "html": html})


#
# CONTACT
#

@app.get("/contact")
async def contact_page(request: Request):
    """
    page that lists contact information
    :return: up message
    """
    folders = get_available_workflows()
    page = "cloudmesh/cc/service/markdown/contact.md"
    import markdown
    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("contact.html",
                                      {"request": request,
                                       "workflowlist": folders,
                                       "html": html})


@app.get("/about")
async def about_page(request: Request):
    """
    page that lists readme as html
    :return: up message
    """
    page = "cloudmesh/cc/service/markdown/about.md"
    import requests
    import markdown
    about = readfile(page)
    html = markdown.markdown(about)
    folders = get_available_workflows()
    return templates.TemplateResponse("about.html",
                                      {"request": request,
                                       "html": html,
                                       "workflowlist": folders})


#
# WORKFLOW
#


@app.get("/workflows", tags=['workflow'])
def list_workflows(request: Request, output: str = None):
    """
    This command returns a list of workflows that is found within
    the server.
    
    :return: list of workflow names
    """

    dict_of_workflow_dicts = dict_of_available_workflows()

    try:

        if output == 'json':
            json_workflow = json.dumps(dict_of_workflow_dicts)
            json_filepath = Shell.map_filename(
                f'~/.cloudmesh/workflow/all-workflows-json.json').path
            writefile(json_filepath, json_workflow)
            return FileResponse(json_filepath)

        elif output == 'csv':
            df = pd.DataFrame(dict_of_workflow_dicts)
            csv_filepath = Shell.map_filename(
                f'~/.cloudmesh/workflow/all-workflows-csv.csv').path

            # stream = io.StringIO()
            response = StreamingResponse(io.StringIO(df.to_csv()),
                                         media_type="text/csv")
            response.headers["Content-Disposition"] = f"attachment; filename=all-workflows-csv.csv"
            return response

        else:
            folders = get_available_workflows()
            return {"workflows": folders}

    except Exception as e:
        return {"message": f"No workflows found"}


# we need to be putting in there whatever we need to be updating.
# 1. upload a.yaml (standalone, doesnt need anything else)
# 1.1 upload a.yaml?name=d
# 2. upload b.yaml (contains b.sh, b.ipynb, b.py, and maybe b.data)
# 2.1 upload b.yaml?name=d
# 2.1 this needs a second part - upload b.sh, b.ipynb, b.py, b.data
# 3. upload directory/* (the * represents the yaml and the scripts)
# 3.1 the name is determined from the yaml file in that directory
# 3.2 upload directory?name=d
# the uploaded workflow is called 'd' (placeholder name)
# 4. upload compressed file (tar) the format is tgz,xz (two different formats)
# 4.1 a.tgz and a.xz which contain whatever is being provided in 1,2,3
# 4.2 they are uncompressed just as if they were to do an individual upload.
# name is optional because the name is determined on what is provided
@app.post("/upload", tags=['workflow'])
async def upload_workflow(file: List[UploadFile] = File(...)):
    """
    uploads a workflow to the fastapi server
    :param file: specified file to be uploaded
    :type file: UploadFile
    :return: success or failure message
    """
    try:
        name = os.path.basename(file[0].filename).split('.')[0]
        runtime_directory = path_expand(f"~/.cloudmesh/workflow/{name}/runtime/")
        yaml_location = path_expand(f"~/.cloudmesh/workflow/{name}/{name}.yaml")
        from pathlib import Path
        runtime_directory = Path(runtime_directory).as_posix()

        if file[0].filename.endswith('.tgz') or \
                file[0].filename.endswith('.xz') or \
                file[0].filename.endswith('.tar.gz') or \
                file[0].filename.endswith('.tar'):

            temporary_location = path_expand(f"./{file[0].filename}")
            temporary_location = Path(temporary_location).as_posix()
            with open(temporary_location, "wb+") as file_object:
                file_object.write(file[0].file.read())

            w = Workflow()
            Shell.mkdir(runtime_directory)
            if file[0].filename.endswith('.tar'):
                command = f'tar --strip-components 1 --force-local -xvf {temporary_location} -C {runtime_directory}'
            else:
                command = f'tar --strip-components 1 --force-local -xvzf {temporary_location} -C {runtime_directory}'
            print(command)
            os.system(command)
            Shell.rm(f'{temporary_location}')
            runtime_yaml_location = os.path.join(runtime_directory, f'{name}.yaml')
            runtime_yaml_location = os.path.normpath(runtime_yaml_location)
            w.load(filename=runtime_yaml_location)
            print(w.yaml)

        elif file[0].filename.endswith('.yaml'):
            Shell.mkdir(runtime_directory)

            print("LOG: Create Workflow at:", yaml_location)
            contents = await file[0].read()

            with open(yaml_location, 'wb') as f:
                f.write(contents)

            w = load_workflow(name)
            print(w.yaml)
    except Exception as e:
        Console.error(e, traceflag=True)
        return {"message": f"There was an error uploading the file {e}"}
    # finally:
    #     await file.close()

    return {"message": f"Successfully uploaded {[files.filename for files in file]}"}


# import requests
#
# url = 'http://127.0.0.1:8000/upload'
# file = {'file': open('images/1.png', 'rb')}
# resp = requests.post(url=url, files=file)
# print(resp.json())

@app.delete("/workflow/{name}", tags=['workflow'])
def delete_workflow(name: str, job: str = None):
    """
    deletes the job in the specified workflow if specified;
    if the job is not specified, then deletes entire workflow
    :param name: name of the workflow
    :type name: str
    :param job: name of the job
    :type job: str
    :return: success or failure message
    """
    if job is not None:
        # if we specify to delete the job
        try:
            w = load_workflow(name)
            # print(w[job])
            w.remove_job(job, state=True)
            return {"message": f"The job {job} was deleted in the workflow {name}"}
        except Exception as e:
            print(e)
            Console.error(e, traceflag=True)
            return {"message": f"There was an error deleting the job '{job}' in workflow '{name}'"}
    else:
        # if we specify to delete the workflow
        try:
            # w = load_workflow(name)
            directory = path_expand(f"~/.cloudmesh/workflow/{name}")
            os.system(f"rm -rf {directory}")
            return {"message": f"The workflow {name} was deleted and the directory {directory} was removed"}
        except Exception as e:
            Console.error(e, traceflag=True)
            return {"message": f"There was an error deleting the workflow '{name}'"}


@app.get("/workflow/{name}", tags=['workflow'])
def get_workflow(request: Request, name: str, job: str = None, output: str = None):
    """
    retrieves a job in a workflow, if specified. if not specified,
    retrieves an entire workflow
    :param name: name of the workflow
    :type name: str
    :param job: name of the job
    :type job: str
    :param output: how to print workflow. can be html or table
    :type output: str
    :return: success or failure message
    """
    try:
        if output == 'html':
            # #result = [os.path.basename(e) for e in result]
            # w = load_workflow(name=name, load_with_graph=True)
            # print(w.dict_of_workflow)
            # df = pd.DataFrame(w.dict_of_workflow)
            # df_html = df.to_html()
            # #html_workflow = Printer.write(table=w_dict, output='html')
            # script_dir = os.path.dirname(os.path.realpath(__file__))
            # script_dir = os.path.join(script_dir, 'templates')
            # script_dir = os.path.join(script_dir, f'{name}-html.html')
            # writefile(script_dir, df_html)
            # return templates.TemplateResponse(f"{name}-html.html", {"request": request})
            w = load_workflow(name=name, load_with_graph=True)
            test = w.table
            data = dict(w.graph.nodes)
            order = ['number',
                     'host',
                     'status',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']
            workflow_html = Printer.dict_html(w.graph.nodes, order=order)
            script_dir = os.path.dirname(os.path.realpath(__file__))
            script_dir = os.path.join(script_dir, 'templates')
            script_dir = os.path.join(script_dir, f'{name}-html.html')
            writefile(script_dir, workflow_html)
            return templates.TemplateResponse(f"{name}-html.html", {"request": request})

        elif output == 'graph':
            filename = Shell.map_filename(
                f'~/.cloudmesh/workflow/{name}/{name}.yaml').path
            w = load_workflow(name=name, load_with_graph=True)
            w.graph.load(filename=filename)
            svg_file = Shell.map_filename(
                f'~/.cloudmesh/workflow/{name}/{name}.svg').path
            w.graph.save(filename=svg_file, colors="status",
                         layout=nx.circular_layout, engine="dot")
            print(w.graph)
            print(w.table)

            return FileResponse(svg_file)

        elif output == 'json':
            w = load_workflow(name)
            w_dict = w.dict_of_workflow
            json_workflow = json.dumps(w_dict)
            json_filepath = Shell.map_filename(f'~/.cloudmesh/workflow/{name}/{name}-json.json').path
            writefile(json_filepath, json_workflow)
            return FileResponse(json_filepath)

        elif output == 'table':
            folders = get_available_workflows()
            w = load_workflow(name)

            order = ['number',
                     'host',
                     'status',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']

            w.create_topological_order()
            workflow_dict = Printer.dict(w.graph.nodes, order=order)
            status_dict = w.analyze_states()

            return templates.TemplateResponse("workflow-table.html",
                                              {"request": request,
                                               "dictionary": w.graph.nodes,
                                               "name_of_workflow": name,
                                               "workflowlist": folders,
                                               "status_dict": status_dict})

        elif output == 'csv':
            w = load_workflow(name)
            w_dict = w.dict_of_workflow
            df = pd.DataFrame(w_dict)
            response = StreamingResponse(io.StringIO(df.to_csv()),
                                         media_type="text/csv")

            response.headers["Content-Disposition"] = f"attachment; filename={name}-csv.csv"
            return response

    except Exception as e:
        print(e)
        Console.error(e, traceflag=True)
        return {"message": f"There was an error with getting the workflow '{name}'"}

    if job is not None:
        try:
            w = load_workflow(name)
            result = w[job]
            return {name: result}
        except Exception as e:
            print(e)
            Console.error(e, traceflag=True)
            return {"message": f"There was an error with getting the job '{job}' in workflow '{name}'"}
    else:
        try:
            w = load_workflow(name)
            return {name: w}
        except Exception as e:
            print(e)
            Console.error(e, traceflag=True)
            return {"message": f"There was an error with getting the workflow '{name}'"}


@app.get("/workflow-graph/{name}")
def get_workflow_graph(request: Request, name: str):
    folders = get_available_workflows()
    svg = f"http://127.0.0.1:8000/workflow/{name}?output=graph"
    import requests
    r = requests.get(svg)
    # r = '''
    # <ul>
    #     <li>
    #         hello
    #     </li>
    # </ul>
    # '''

    print(r.text)
    w = load_workflow(name)
    status_dict = w.analyze_states()
    return templates.TemplateResponse("workflow-graph.html",
                                      {"request": request,
                                       "svg": r.text,
                                       "name_of_workflow": name,
                                       "workflowlist": folders,
                                       "status_dict": status_dict})


@app.get("/workflow-graph?{name}", tags=['workflow'])
def retrieve_workflow_graph(request: Request,
                            name: str,
                            job: str = None,
                            output: str = None):
    """
    retrieves a workflow graph
    :param name: name of the workflow
    :type name: str
    :param job: name of the job
    :type job: str
    :param output: how to print workflow. can be html or table
    :type output: str
    :return: success or failure message
    """
    folders = get_available_workflows()
    filename = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name}/{name}.yaml').path
    w = load_workflow(name=name, load_with_graph=True)
    w.graph.load(filename=filename)
    svg_file = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name}/runtime/{name}.svg').path
    w.graph.save(filename=svg_file, colors="status",
                 layout=nx.circular_layout, engine="dot")
    print(w.graph)
    print(w.table)

    return templates.TemplateResponse("workflow-graph.html",
                                      {"request": request,
                                       "dictionary": w.graph.nodes,
                                       "name_of_workflow": name,
                                       "workflowlist": folders})


@app.get("/run/{name}", tags=['workflow'])
def run_workflow(request: Request, name: str, run_type: str = "topo"):
    """
    runs a specified workflow according to provided run type
    :param name: name of workflow
    :type name: str
    :param run_type: type of run, either topo or parallel
    :type run_type: str
    :return: success or exception message
    """
    w = load_workflow(name)
    os.chdir(os.path.dirname(w.filename))

    try:
        if run_type == "topo":
            threading.Thread(target=w.run_topo, kwargs={'show': True}).start()
            #w.run_topo(show=True)
        else:
            threading.Thread(target=w.run_parallel, kwargs={'show': True}).start()
            #w.run_parallel(show=True)
        #return {"Success": "Workflow ran successfully"}
        return RedirectResponse(url=f'/workflow-running/{w.name}')
    except Exception as e:
        print("Exception:", e)

@app.get("/workflow-running/{name}")
def watch_running_workflow(request: Request,
                            name: str,
                            job: str = None,
                            output: str = None):
    """
    page for watching a workflow that has been started
    """

    folders = get_available_workflows()
    w = load_workflow(name)
    runtime_yaml_to_read = readfile(w.runtime_filename)
    yaml_file = yaml.safe_load(runtime_yaml_to_read)
    progress_and_job = []
    for node_name, node_items in yaml_file['workflow']['nodes'].items():
        progress_and_job.append(tuple([node_name, node_items['progress']]))
    status_dict = w.analyze_states()
    return templates.TemplateResponse("workflow-running.html",
                                      {"request": request,
                                       "dictionary": w.graph.nodes,
                                       "name_of_workflow": name,
                                       "workflowlist": folders,
                                       "status_dict": status_dict})

@app.post("/workflow/{name}", tags=['workflow'])
def add_job(name: str, job: Jobpy):
    """curl -X 'POST' 'http://127.0.0.1:8000/workflow/workflow?job=c&user=gregor&host=localhost&kind=local&status=ready&script=c.sh' -H 'accept: application/json'/
    This command adds a node to a workflow. with the specified arguments. A check
                is returned and the user is alerted if arguments are missing
                arguments are passed in ATTRIBUTE=VALUE fashion.
                if the name of the workflow is omitted, the default workflow is used.
                If no job name is specified, an automated number that is kept in the
                config.yaml file will be used and the name will be job-n

    :param name: the name of the workflow
    :type name: str
    :param job: the specifications and characteristics of the job
    :type job: Jobpy
    :return: returns jobs within the specified workflow
    """

    # cms cc workflow service add [--name=NAME] --job=JOB ARGS...
    # cms cc workflow service add --name=workflow --job=c user=gregor host=localhost kind=local status=ready script=c.sh
    # curl -X 'POST' 'http://127.0.0.1:8000/workflow/workflow?job=c&user=gregor&host=localhost&kind=local&status=ready&script=c.sh' -H 'accept: application/json'

    w = load_workflow(name)

    try:
        w.add_job(name=job.name,
                  user=job.user,
                  host=job.host,
                  label=job.label,
                  kind=job.kind,
                  status=job.status,
                  progress=job.progress,
                  script=job.script)
        w.add_dependencies(f"{job.parent},{job.name}")
        w.save_with_state(w.filename)
    except Exception as e:
        print("Exception:", e)

    return {"jobs": w.jobs}

#
# QUEUES
#
# @app.get("/queues/", response_class=HTMLResponse)
# async def list_queues(request: Request):
#     global q
#     return templates.TemplateResponse('templates/queues.html',
#                                       {"request": request,
#                                        "queues": q.queues})
#
#
# #TODO: fix
# @app.post("/queue")
# async def add_queue(name: str):
#     global q
#     q.create(name=name)
#     return {
#         "queues": q.queues
#     }
#
# # TODO this may not be right
# @app.delete("/queue/{name}")
# async def delete_queue(name: str):
#     global q
#     q.remove(name)
#     return {
#         "queues": q.queues
#     }
#
#
# #
# # JOBS
# #
#
# #TODO: fix
# @app.post("/job")
# async def add_job(name: str, job: str, command: str):
#     global q
#     q.add(name=name, job=job, command=command)
#     return {
#         "jobs": q.queues[name]
#     }
#
# # TODO this may not be right
# @app.delete("/job/{queue}/{name}")
# async def delete_job(name: str, queue:str):
#     global q
#     q.remove(name)
#     return {
#         "jobs": q.queues[name]
#     }
#
# @app.get("/jobs/{queue}", response_class=HTMLResponse)
# async def list_jobs(request: Request, queue: str):
#     global q
#     jobs = []
#     for q in q.queues:
#         if q == queue:
#             for job in q.queues[queue]:
#                 jobs.append(q.queues[queue][job])
#     order = q.queues[queue][job][0:1]
#     order = [word.capitalize() for word in order]
#     Console.error(str(order))
#
#     return templates.TemplateResponse("templates/item.html",
#                                       {"request": request,
#                                        "no": no,
#                                        "jobs": jobs,
#                                        "order": order})
#
#
# @app.get("/job/{queue}/{job}", response_class=HTMLResponse)
# async def read_job(queue: str, job: str):
#     global q
#     result = Printer.attribute(q.queues[queue][job], output='html')
#     name = q.queues[queue][job]["name"]
#     d = f"<h1>{name}</h1>"
#     d += "<table>"
#     d += f"<tr> <th> attribute </th><th> value </th> </tr>"
#
#     for attribute in q.queues[queue][job]:
#         value = q.queues[queue][job][attribute]
#         d += f"<tr> <td> {attribute} </td><td> {value} </td> </tr>"
#     d += "</table>"
#     result = d
#     print(Printer.attribute(q.queues[queue][job]))
#     print(result)
#
#     page = f"""
#     <html>
#         <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.css">
#         <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.js"></script>
#         <head>
#             <title>Some HTML in here</title>
#         </head>
#         <body>
#             {result}
#         </body>
#     </html>
#     """
#     return page
