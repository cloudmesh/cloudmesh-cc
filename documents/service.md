# Cloudmesh-cc Service Quickstart

To run the service with the GUI, type the following command:

```bash
$ cms cc start
```

This starts the uvicorn server and runs the `service.py` file in
the `cloudmesh-cc` repository. It will take you to this message:

`{"msg":"cloudmesh.cc is up"}`

In the URL, type `/docs` in front, which takes you to the GUI.

`http://127.0.0.1:8000/docs`

![Service GUI Using FastAPI](../images/fastapi-service.png)

From here, you can list your current workflows, delete workflows,
add workflows and jobs, and run them from this site.

## Nomenclature

* Replace `{WORKFLOW_NAME}` with the name of the Workflow you want to perform
  the operation on. These Workflows can be viewed as YAML files in your
  `~/.cloudmesh/workflow` folder.

* Replace `JOB_NAME` with a job name you want to use

## Using Requests

There are three type of requests that can be used. GET, POST, and
DELETE. The syntax is similar but parameters are slightly different.
The following are a list of the methods used in the service.

* GET `/workflows` List Workflows
* POST `/workflow/upload` Upload Workflow
* GET `/workflow/{name}` Get Workflow
* POST `/workflow/{name}` Add Job
* DELETE `/workflow/{name}` Delete Workflow
* GET `/workflow/run/{name}` Run Workflow

To use any of these methods, you must import requests.


```python
import requests

# GET `/workflows` List Workflows
r = requests.get("/workflows")
print(r.json()) # prints the name of all the workflows

# POST `/workflow/upload` Upload Workflow
files = {"file": open("{FILENAME}","rb")} # replace the file with the file name you want to use
r = requests.post("/workflow/upload",files=files)

# GET `/workflow/{name}` Get Workflow
r = requests.get("/workflow/{WORKFLOW_NAME}?job={JOB_NAME}") # to access a single job
r = requests.get("/workflow/{WORKFLOW_NAME}") # to acess the entire workflow

# POST `/workflow/{name}` Add Job
job = ''' {"name": "string",
            "user": "string",
            "host": "string",
            "label": "string",
            "kind": "string",
            "status": "string",
            "progress": 0,
            "script": "string",
            "pid": 0,
            "parent": "string"} '''
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
}

r = requests.post("/workflow/{WORKFLOW_NAME}",data=job,headers=headers)

# DELETE `/workflow/{name}` Delete Workflow
r = requests.delete("/workflow/{WORKFLOW_NAME}")

# GET `/workflow/run/{name}` Run Workflow
r = requests.get("/workflow/run/{WORKFLOW_NAME}")
```

