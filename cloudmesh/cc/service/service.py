import logging
from cloudmesh.cc.queue import Queues
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Printer import Printer
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import pkg_resources
from cloudmesh.common.console import Console
import os
from cloudmesh.common.util import  path_expand


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

<<<<<<< HEAD
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
    return {"msg": "Cloudmesh hello universe cc"}

@app.get("/items", response_class=HTMLResponse)
async def item_table(request: Request):
    return templates.TemplateResponse("templates/table.html",
                                      {"request": request})

#
# WORKFLOW
#


#
# @app.post("/workflow")
# async def upload(file: UploadFile = File(...)):
#     try:
#         contents = await file.read()
#         with open(file.filename, 'wb') as f:
#             f.write(contents)
#         w = Workflow()
#         w.save(filename=file.filename)
#     except Exception:
#         return {"message": "There was an error uploading the file"}
#     finally:
#         await file.close()
#
#     return {"message": f"Successfuly uploaded {file.filename}"}

#
# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=8000)
# test.py
#
# import requests
#
# url = 'http://127.0.0.1:8000/upload'
# file = {'file': open('images/1.png', 'rb')}
# resp = requests.post(url=url, files=file)
# print(resp.json())

def setup_workflow(name:str):
    if os.path.exists(f"{name}.yaml"):
        directory=path_expand(f".")
    else:
        directory = path_expand(f"~./cloudmesh/workflow/{name}")
    w = Workflow(name=name, filename=f"{directory}/{name}.yaml")
    return w

@app.get("/workflows/")
def list_workflows():
    return{"name": "implementme get multiple"}

@app.get("/workflow/{name}")
def get_workflow(name:str):
    w = setup_workflow(name)
    return {"name": "implementme delete"}

@app.delete("/workflow/{name}")
def delete_workflow(name:str):
    w = setup_workflow(name)
    # remove the entire workflow

    return{"name": "implementme delete"}

@app.delete("/workflow/{name}/{job}")
def delete_workflow(name:str, job:str):
    w = setup_workflow(name)
    # how to remove an named job form the workflow
    #w.remove(job)
    return{"name": "implementme delete"}


wfdescription =\
"""
adds a workflow with the given name from data included in the filename.
the underlying database will use that name and if not explicitly
specified the location of the database will be
`~/.cloudmesh/workflow/NAME/NAME.yaml`
To identify the location a special configuration file will be placed in
`~/.cloudmesh/workflow/config.yaml` that contains the location of
the directories for the named workflows.

* **name**: name of the workflow to be added
* *return* boolean
"""
@app.post("/workflow/{name}",
          summary="Add a workflow from a file",
          description=wfdescription
          )
async def add_workflow(name: str, **kwargs) -> bool:
    """
        adds a workflow with the given name from data included in the filename.
                the underlying database will use that name and if not explicitly
                specified the location of the database will be
                `~/.cloudmesh/workflow/NAME/NAME.yaml`
                To identify the location a special configuration file will be placed in
                `~/.cloudmesh/workflow/config.yaml` that contains the location of
                the directories for the named workflows.

    :param name:
    :param kwargs:
    :return: bool=True if add was successful
    """
    params = dict(kwargs if kwargs else {})
    dir = params["directory"] if params["directory"] else f"~./cloudmesh/workflow/{name}"
    if os.path.exists(path_expand(f"{dir}/{name}.yaml")):
        Console.warning("Workflow already exists. Exiting.")
        return False

    if not kwargs:
        w = setup_workflow(name)
    else:
        us = None if "user" not in params else params["user"]
        ho = None if "host" not in params else params["host"]
        w = Workflow(name=name, filename=f"{dir}/{name}.yaml",user=us,host=ho)
    # w.save()
    return True



@app.post("/workflow/{name}/{job}")
async def add_job(workflow: str, **kwargs) -> bool:
    """
    This command ads a job. with the specified arguments. A check
                is returned and the user is alerted if arguments are missing
                arguments are passed in ATTRIBUTE=VALUE fashion.
                if the name of the workflow is omitted the default workflow is used.
                If no cob name is specified an automated number that is kept in the
                config.yaml file will be used and the name will be job-n

    :param workflow: the name of the workflow
    :param kwargs: the arguments to pass into the job
    :return:
    """


    # params = dict(kwargs = kwargs if kwargs else {})
    # na = None if "name" not in params else params["name"]
    # us = None if "user" not in params else params["user"]
    # ho = None if "host" not in params else params["host"]
    # la = None if "label" not in params else params["label"]
    # ki = "local" if "kind" not in params else params["kind"]
    # st = "ready" if "status" not in params else params["status"]
    # pr = 0 if "progress" not in params else params["progress"]
    # sc = None if "script" not in params else params["script"]
    # pi = None if "pid" not in params else params["pid"]

    w = setup_workflow(workflow)

    try:
        w.add_job(kwargs)
        return True
    except Exception as e:
        print(e)
        return False



#
# QUEUES
#
@app.get("/queues/", response_class=HTMLResponse)
async def list_queues(request: Request):
    global q
    return templates.TemplateResponse('templates/queues.html',
                                      {"request": request,
                                       "queues": q.queues})


#TODO: fix
@app.post("/queue")
async def add_queue(name: str):
    global q
    q.create(name=name)
    return {
        "queues": q.queues
    }

# TODO this may not be right
@app.delete("/queue/{name}")
async def delete_queue(name: str):
    global q
    q.remove(name)
    return {
        "queues": q.queues
    }


#
# JOBS
#

#TODO: fix
@app.post("/job")
async def add_job(name: str, job: str, command: str):
    global q
    q.add(name=name, job=job, command=command)
    return {
        "jobs": q.queues[name]
    }

# TODO this may not be right
@app.delete("/job/{queue}/{name}")
async def delete_job(name: str, queue:str):
    global q
    q.remove(name)
    return {
        "jobs": q.queues[name]
    }

@app.get("/jobs/{queue}", response_class=HTMLResponse)
async def list_jobs(request: Request, queue: str):
    global q
    jobs = []
    for q in q.queues:
        if q == queue:
            for job in q.queues[queue]:
                jobs.append(q.queues[queue][job])
    order = q.queues[queue][job][0:1]
    order = [word.capitalize() for word in order]
    Console.error(str(order))

    return templates.TemplateResponse("templates/item.html",
                                      {"request": request,
                                       "id": id,
                                       "jobs": jobs,
                                       "order": order})


@app.get("/job/{queue}/{job}", response_class=HTMLResponse)
async def read_job(queue: str, job: str):
    global q
    result = Printer.attribute(q.queues[queue][job], output='html')
    name = q.queues[queue][job]["name"]
    d = f"<h1>{name}</h1>"
    d += "<table>"
    d += f"<tr> <th> attribute </th><th> value </th> </tr>"

    for attribute in q.queues[queue][job]:
        value = q.queues[queue][job][attribute]
        d += f"<tr> <td> {attribute} </td><td> {value} </td> </tr>"
    d += "</table>"
    result = d
    print(Printer.attribute(q.queues[queue][job]))
    print(result)

    page = f"""
    <html>
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.css">
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.js"></script>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            {result}
        </body>
    </html>
    """
    return page
