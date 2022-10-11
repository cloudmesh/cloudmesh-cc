# REST

Cloudmesh cc can be interfaced with Representational
State Transfer (REST) by using Curl commands. REST
is advantageous as it can be used with programming
languages other than Python.

To use this feature, ensure that the FastAPI server is 
online with the following commands:

```bash
cd ~/cm/cloudmesh-cc
cms cc start
```

## List Workflows Available on Local Computer

The following command returns a dict that lists each
available workflow.

```bash
curl -X 'GET' \
    'http://127.0.0.1:8000/workflows' \
    -H 'accept: application/json'
```

## Upload a Workflow

There are different ways to upload a new workflow to
cloudmesh-cc, by specifying one of the following:

- a directory that contains the scripts and yaml

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/workflow?directory=~/cm/cloudmesh-cc/tests/workflow-example' \
    -H 'accept: application/json' \
    -d ''
```

- an archive file in tgz, xz, tar.gz, or tar format that contains the scripts
and yaml

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/workflow?archive=ThePathToYourArchiveFile' \
    -H 'accept: application/json' \
    -d ''
```

- or a yaml file that specifies what jobs to run.

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/workflow?yaml=~/cm/cloudmesh-cc/tests/workflow-example/workflow-example.yaml' \
    -H 'accept: application/json' \
    -d ''
```

## Delete a Workflow

The following command deletes a preexisting workflow
from the local computer.

To use it, replace `workflow-example` with the workflow
you wish to delete.

```bash
curl -X 'DELETE' \
    'http://127.0.0.1:8000/workflow/workflow-example' \
    -H 'accept: application/json'
```

## Retrieve a Workflow

The following command retrieves a workflow and its
configuration, such as the directory where it resides, 
the jobs that it contains, the colors of the statuses,
and more.

To use it, replace `workflow-example` with the workflow
you wish to retrieve.

```bash
curl -X 'GET' \
    'http://127.0.0.1:8000/workflow/workflow-example' \
    -H 'accept: application/json'
```

## Run a Workflow

The following command runs a workflow.

To use it, replace `workflow-example` with the workflow
you wish to run. Additionally, to hide the graph of the
workflow as it is run, replace `show=True` with `show=False`.

```bash
curl -X 'GET' \
    'http://127.0.0.1:8000/workflow/run/workflow-example?show=True' \
    -H 'accept: application/json'
```

## Add a Job to a Workflow

The following command adds a new job to a preexisting workflow.

The only required parameter is the job parameter, which specifies
the name of the job. The other optional parameters include the
user, host, label, kind, status, progress, and script. To use
the command, replace `workflow-example` with the workflow you
wish to change. Additionally, change the other parameters, as desired.

```bash
curl -X 'POST' \
    'http://127.0.0.1:8000/workflow/job/workflow-example?job=myJob&user=aPerson&host=local&kind=local&status=ready&script=aJob.sh&progress=0&label=aLabel' \
    -H 'accept: application/json'
```
