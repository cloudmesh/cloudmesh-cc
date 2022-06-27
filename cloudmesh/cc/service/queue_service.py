from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import Request
from cloudmesh.cc.queue import Queues
import logging
from cloudmesh.common.Printer import Printer
import uvicorn
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pkg_resources
from cloudmesh.common.console import Console


app = FastAPI()

q = Queues(database='yamldb')

template_dir = pkg_resources.resource_filename("cloudmesh.cc", "service")
templates = Jinja2Templates(directory=template_dir)

print('Current structure:', q.queues)
print('Current file: ', q.db)


@app.get("/")
async def home():
    return {"cloudmesh-queue": "running"}


# @app.get("/queues/")
# async def info():
#     return {
#         "name": q.name,
#         "queues": q.queues,
#         "file": q.db
#     }

@app.get("/queues/{id}", response=HTMLResponse)
async def info(request: Request, id: str):
    global q
    return templates.TemplateResponse('templates/queue.html',
                                      {"request": request,
                                       "id" : id,
                                       "name": q.name,
                                       "queues": q.queues,
                                       "file": q.db})




@app.get("/queue/")
async def get_queue(name: str):
    return {"queue": q[name]}

@app.get("/job/")

async def get_queue(name: str):
    return {"job": "todo"}

@app.post("/add/")
async def create_item(queuename: str, jobname: str, command:str):
    q.add(name=jobname, command=command)

