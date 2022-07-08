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


#
# ROUTES

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
    return templates.TemplateResponse('templates/workflow.html',
                                      {"workflow": w.table})

@app.delete("/workflow/{name}")
def delete_workflow(name:str):
    if os.path.exists(f"{name}.yaml"):
        w = Workflow(name=name, filename=f"{name}.yaml", user=None, host=None)
    else:
        w = Workflow(name=name, filename=f"~/.cloudmesh/workflow/{name}/{name}.yaml")
    # w.remove()

    return{"name": "implementme delete"}


wfdescription =\
"""adds a workflow with the given name from data included in the filename.
the underlaying database will use that name and if not explicitly
specified the location of the data base will be
`~/.cloudmesh/workflow/NAME/NAME.yaml`
To identify the location a special configuratiion file will be placed in
`~/.cloudmesh/workflow/config.yaml` that contains the loaction of
the directories for the named workflows.

* markdown??
* h
"""

import textwrap
@app.post("/workflow/{name}",
          summary="Add a workflow from a file",
          description=wfdescription
          )
async def add_job(name: str, workflow: str, **argv) -> bool:
    """
    adds a workflow with the given name from data included in the filename.
            the underlaying database will use that name and if not explicitly
            specified the location of the data base will be
            `~/.cloudmesh/workflow/NAME/NAME.yaml`
            To identify the location a special configuratiion file will be placed in
            `~/.cloudmesh/workflow/config.yaml` that contains the loaction of
            the directories for the named workflows.

    :param name:
    :param workflow:
    :param argv:
    :return: boolean
    """

    """
    cc workflow service add [--name=NAME] [--directory=DIR] FILENAME
                adds a workflow with the given name from data included in the filename.
                the underlaying database will use that name and if not explicitly
                specified the location of the data base will be
                ~/.cloudmesh/workflow/NAME/NAME.yaml
                To identify the location a special configuratiion file will be placed in
                ~/.cloudmesh/workflow/config.yaml that contains the loaction of
                the directories for the named workflows.
    """

    """
    def get_data(endpoint:str='my_endpoint', *args, **kwargs):
    q = dict(
        args = list(args) if args else [], 
        kwargs = kwargs if kwargs else {}
    )
    return True     # success status
    """


    # TODO: **argv in fastapi
    w = setup_workflow(name)
    # w.add()
    return {
        "name": "implement me"
    }


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
async def list_jobs(queue: str):
    global q
    jobs = []
    for queue in q.queues:
        for job in q.queues[queue]:
            jobs.append(q.queues[queue][job])

    result = Printer.write(jobs, output='html')
    result = result.replace('\n', '')

    page = f"""
        <html>
            <head>
                <title>Some HTML in here</title>
            </head>
            <body>
                {result}
            </body>
        </html>
        """
    return page


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
