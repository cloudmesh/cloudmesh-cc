from fastapi import FastAPI
import logging
from cloudmesh.cc.queue import Queues
from cloudmesh.common.Printer import Printer
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI

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
    return q

q = test_run()

app = FastAPI()


@app.get("/")
async def read_home():
    return {"msg": "Hello World"}


@app.get("/jobs/", response_class=HTMLResponse)
async def read_items():
    global q
    n = []
    for queue in q.queues:
        for job in q.queues[queue]:
            n.append(q.queues[queue][job])

    result = Printer.write(n, output='html')
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
    print(Printer.attribute(q.queues[queue][job]))
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