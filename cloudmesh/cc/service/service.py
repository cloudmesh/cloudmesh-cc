import logging

import networkx as nx

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
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

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

from cloudmesh.cc.__version__ import version as cm_version

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

def load_workflow(name: str, load_with_graph = False) -> Workflow:
    """
    loads a workflow corresponding to given name
    :param name:
    :type name: str
    :return: loaded workflow
    :rtype: Workflow
    """
    filename = Shell.map_filename(f"~/.cloudmesh/workflow/{name}/{name}.yaml").path
    w = Workflow(filename=filename, load=True)
    #w.__init__(filename=filename)
    #w.load(filename=filename)
    if load_with_graph:
        pass
        #w.graph.save_to_file(filename=f"{name}.svg")
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
    print('aa')
    print(os.getcwd())
    folders = get_available_workflows()
    return templates.TemplateResponse("home.html", {"request": request, "workflowlist": folders})

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
    return templates.TemplateResponse("contact.html",
                                      {"request": request,
                                       "workflowlist": folders})

@app.get("/about")
async def about_page(request: Request):
    """
    page that lists readme as html
    :return: up message
    """
    folders = get_available_workflows()
    return templates.TemplateResponse("about.html",
                                {"request": request,
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

            #stream = io.StringIO()
            response = StreamingResponse(io.StringIO(df.to_csv()),
                                         media_type="text/csv")
            response.headers["Content-Disposition"] = f"attachment; filename=all-workflows-csv.csv"
            return response

        else:
            folders = get_available_workflows()
            return {"workflows": folders}

    except Exception as e:
        return {"message": f"No workflows found"}


@app.post("/upload", tags=['workflow'])
async def upload_workflow(file: UploadFile = File(...)):
    """
    uploads a workflow to the fastapi server
    :param file: specified file to be uploaded
    :type file: UploadFile
    :return: success or failure message
    """
    try:
        name = os.path.basename(file.filename).replace(".yaml", "")
        directory = path_expand(f"~/.cloudmesh/workflow/{name}")
        location = path_expand(f"~/.cloudmesh/workflow/{name}/{name}.yaml")
        if os_is_windows():
            Shell.mkdir(directory)
            os.system(f"mkdir {directory}")
        else:
            os.system(f"mkdir -p {directory}")
        print("LOG: Create Workflow at:", location)
        contents = await file.read()

        with open(location, 'wb') as f:
            f.write(contents)

        w = load_workflow(name)
        print(w.yaml)
    except Exception as e:
        Console.error(e, traceflag=True)
        return {"message": f"There was an error uploading the file {e}"}
    finally:
        await file.close()

    return {"message": f"Successfully uploaded {file.filename}"}


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
                
            return templates.TemplateResponse("workflow-table.html",
                                              {"request": request,
                                               "dictionary": w.graph.nodes,
                                               "name_of_workflow": name,
                                               "workflowlist": folders})

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


@app.get("/run/{name}", tags=['workflow'])
def run_workflow(name: str, run_type: str = "topo"):
    """
    runs a specified workflow according to provided run type
    :param name: name of workflow
    :type name: str
    :param run_type: type of run, either topo or parallel
    :type run_type: str
    :return: success or exception message
    """
    w = load_workflow(name)
    try:
        if run_type == "topo":
            w.run_topo(show=True)
        else:
            w.run_parallel(show=True)
        return {"Success": "Workflow ran successfully"}
    except Exception as e:
        print("Exception:", e)


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
        w.add_job(name=job.name, user=job.user, host=job.host, label=job.label,
                  kind=job.kind, status=job.status, progress=job.progress, script=job.script)
        w.add_dependencies(f"{job.parent},{job.name}")
        w.save_with_state(w.filename)
    except Exception as e:
        print("Exception:",e)

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
