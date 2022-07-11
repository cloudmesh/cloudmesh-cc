import logging
from cloudmesh.cc.queue import Queues
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Printer import Printer
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import File
from fastapi import UploadFile

from fastapi.staticfiles import StaticFiles
import pkg_resources
from cloudmesh.common.console import Console
import os
from cloudmesh.common.util import  path_expand
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
import glob

def test_run():
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


q = test_run()

app = FastAPI()

#
# REGISTER template and static dir
#

statis_dir = pkg_resources.resource_filename("cloudmesh.cc", "service/static")

app.mount("/static", StaticFiles(directory=statis_dir), name="static")

template_dir = pkg_resources.resource_filename("cloudmesh.cc", "service")
templates = Jinja2Templates(directory=template_dir)

#
# ROUTES
#

@app.get("/item/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    global q
    jobs = []
    for queue in q.queues:
        for job in q.queues[queue]:
            jobs.append(q.queues[queue][job])
    order = q.queues[queue][job].keys()
    order = [word.capitalize() for word in order]
    Console.error(str(order))

    return templates.TemplateResponse("templates/item.html",
                                      {"request": request,
                                       "id": id,
                                       "jobs": jobs,
                                       "order": order})

@app.get("/")
async def home():
    return {"msg": "Cloudmesh b cc"}

@app.get("/items", response_class=HTMLResponse)
async def item_table(request: Request):
    return templates.TemplateResponse("templates/table.html",
                                      {"request": request})

#
# WORKFLOW
#

def load_workflow(name:str):
    filename = path_expand(f"~/.cloudmesh/workflow/{name}/{name}.yaml")
    w = Workflow(name=name, filename=filename)
    # w.load(filename)
    return w

@app.get("/workflows")
def list_workflows():
    """
    this command reacts dependent on which options we specify
                If we do not specify anything the workflows will be listed.
                If we specify a workflow name only that workflow will be listed
                If we also specify a job the job will be listed.
                If we only specif the job name, all jobs with that name from all
                workflows will be returned.
    :param name:
    :param job:
    :return:
    """

    try:
        directory = path_expand(f"~/.cloudmesh/workflow/")
        result = glob.glob(f"{directory}/*")
        result = [os.path.basename(e) for e in result]
        return{"workflows": result}
    except Exception as e:
        return {"message": f"No workflows found"}


@app.post("/upload")
async def upload_workflow(file: UploadFile = File(...)):
    try:
        name = os.path.basename(file.filename).replace(".yaml", "")
        directory = path_expand(f"~/.cloudmesh/workflow/{name}")
        location = f"{directory}/{name}.yaml"
        if os_is_windows():
            Shell.mkdir(directory)
        else:
            os.system(f"mkdir -p {directory}")
        print("LOG: Create Workflow at:", location)
        contents = await file.read()

        with open(location, 'wb') as f:
            f.write(contents)

        w = load_workflow(name)
        print(w.yaml)
    except Exception as e:
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

@app.delete("/workflow/{name}")
def delete_workflow(name:str, job: str=None):
    """
    deletes the job in the specified workflow if specified and the workflow otherwise
    :param name:
    :param job:
    :return:
    """
    if job is not None:
    # if we specify to delete the job
        try:
            w = load_workflow(name)
            # print(w[job])
            w.remove_job(job)
            return {"message": f"The job {job} was deleted in the workflow {name}"}
        except Exception as e:
            return {"message": f"There was an error deleting the job '{job}' in workflow '{name}'"}
    else:
    # if we specify to delete the workflow
        try:
            # w = load_workflow(name)
            directory = path_expand(f"~/.cloudmesh/workflow/{name}")
            os.system(f"rm -r {directory}")
            return {"message": f"The workflow {name} was deleted and the directory {directory} was removed"}
        except Exception as e:
            return {"message": f"There was an error deleting the workflow '{name}'"}


@app.get("/workflow/{name}")
def get_workflow(name: str, job: str = None):
    if job is not None:
        try:
            w = load_workflow(name)
            print (w.yaml)
            result = w[job]
            return {name: result}
        except Exception as e:
            return {"message": f"There was an error with getting the job '{job}' in workflow '{name}'"}
    else:
        try:
            w = load_workflow(name)
            print(w.yaml)
            return {name: w}
        except Exception as e:
            return {"message": f"There was an error with getting the workflow '{name}'"}


@app.post("/workflow/{name}")
async def add_job(name: str, **kwargs) -> bool:
    """curl -X 'POST' 'http://127.0.0.1:8000/workflow/workflow?job=c&user=gregor&host=localhost&kind=local&status=ready&script=c.sh' -H 'accept: application/json'/
    This command adds a node to a workflow. with the specified arguments. A check
                is returned and the user is alerted if arguments are missing
                arguments are passed in ATTRIBUTE=VALUE fashion.
                if the name of the workflow is omitted the default workflow is used.
                If no cob name is specified an automated number that is kept in the
                config.yaml file will be used and the name will be job-n

    :param workflow: the name of the workflow
    :param kwargs: the arguments to pass into the job
    :return:
    """


    # cms cc workflow service add [--name=NAME] --job=JOB ARGS...
    # cms cc workflow service add --name=workflow --job=c user=gregor host=localhost kind=local status=ready script=c.sh
    # curl -X 'POST' 'http://127.0.0.1:8000/workflow/workflow?job=c&user=gregor&host=localhost&kind=local&status=ready&script=c.sh' -H 'accept: application/json'

    w = get_workflow(name)
    print(w.yaml)
    print(kwargs)
    # for attribute in ["job","user","host"]:
    #     if attribute not in kwargs:
    #         print("error")
    #         # return the error object in fastapi
    #
    # w = load_workflow(name)
    #
    # try:
    #     w.add_job(kwargs)
    #     return True
    # except Exception as e:
    #     print(e)
    #     return False



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
#                                        "id": id,
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
