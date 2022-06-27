import logging
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Printer import Printer
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles
import pkg_resources
from cloudmesh.common.console import Console

def test_run():
    kind = 'yamldb'
    q = Queues(filename='~/.cloudmesh/queue/queuetest1', database=kind)
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
# @app.get("/abdul/{id}", response_class=HTMLResponse)
# async def read_anduhl(request: Request, id: str):
#     global q
#     jobs = []
#     for queue in q.queues:
#         for job in q.queues[queue]:
#             jobs.append(q.queues[queue][job])
#
#     return templates.TemplateResponse("templates/abdul.html",
#                                       {"request": request,
#                                        "id": id,
#                                        "jobs": jobs})

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

@app.get("/queues", response_class=HTMLResponse)
async def info(request: Request):
    return templates.TemplateResponse('templates/queue.html',
                                      {"request": request,
                                       "queues": q.queues})



@app.get("/table", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("templates/table.html",
                                      {"request": request})

@app.get("/")
async def read_home():
    return {"msg": "Hello World"}

@app.post("/postQueue")
async def add_queue(name:str):
    global q
    q.create(name=name)
    return {
        "Queues": q.queues
    }


@app.post("/postJob")
async def add_job(name:str, job:str, command:str):
    global q
    q.add(name=name, job=job, command=command)
    return {
        "Queue_Jobs": q.queues[name]
    }

@app.delete("/deleteJob/{job_name}")
async def delete_job(job_name:str):
    global q
    # not implemented yet
    return {
        "Queue_Jobs": q.queues[name]
    }

@app.delete("/deleteQueue/{job_name}")
async def delete_job(queue_name:str):
    global q
    q.remove(queue_name)
    return {
        "Queues": q.queues
    }


@app.get("/jobs/", response_class=HTMLResponse)
async def read_items():
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
async def read_job(queue:str, job:str):
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

