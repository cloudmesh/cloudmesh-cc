git add from fastapi import FastAPI
import logging
from cloudmesh.cc.queue import Queues

app = FastAPI()

q = Queues(name='queue')

print('Structure name: ', q.name)
print('Current structure:', q.queues)
print('Current file: ', q.db)


@app.get("/")
async def home():
    return {"cloudmesh-queue": "running"}


@app.get("/queues/")
async def info():
    return {
        "name": q.name,
        "queues": q.queues,
        "file": q.db
    }


@app.get("/queue/")
async def get_queue(name: str):
    return {"queue": q[name]}

@app.get("/job/")
async def get_queue(name: str):
    return {"job": "todo"}

@app.post("/add/")
async def create_item(queuename: str, jobname: str, command:str):
    q.add(name=jobname, command=command)

