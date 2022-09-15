# Workflow Quickstart Menu

It assumes that you have cloudmesh cc installed 

```bash
pip install cloudmesh-cc
```

We also assume you start the service with

```bash
cms cc start --reload
```

## Upload and run a workflow embedded in a tar file

### Create tar file

```bash
mkdir -p /tmp/workflow
cp tests/workflows/workflow.yaml /tmp/workflow
cp tests/workflow-sh/*.sh /tmp/workflow
tar -C /tmp/workflow -cf workflow.tar .
```

### Upload via `curl`

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload?tar=workflow.tar' \
  -H 'accept: application/json' \
  -d ''
```

### Upload via /docs

Navigate to `http://127.0.0.1:8000/docs` and use
the POST Upload method

Please, click `Try it out`
and then enter `/tmp/workflow/workflow.tar` in the
`tar` field and then click Execute

To run, navigate to homepage at `http://127.0.0.1:8000/` and
click the workflow on the left side. Then click Run

TODO: do the same thing here as we do in upload a workflow with
scripts but instead use the tar upload


## Upload a dir that contains workflow yaml and scripts

### Creating a simple example

First let us create a simple example. We assume you are standing in
the cloudmesh-cc directory.  Let us check it out with

```bash
git clone https://github.com/cloudmesh/cloudmesh-cc.git
cd cloudmesh-cc
```

Now let us use one of the default test workflows and copy it into a
temporary directory


```bash
mkdir -p /tmp/workflow
cp tests/workflows/workflow.yaml /tmp/workflow
cp tests/workflow-sh/*.sh /tmp/workflow
```

Now we can test various ways on how to interact with the service

### Upload via `curl`

A workflow can be uploaded easily with a curl command from the commandline.
On the commandline execute:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload?directory=/tmp/workflow' \
  -H 'accept: application/json' \
  -d ''
```

TODO: on windows it also should work with / and not \ We make explicit note here
when using a drive we do /c/ ....

### Upload via /docs

Navigate to `http://127.0.0.1:8000/docs` and use
the POST Upload method

Click `Try it out` and then enter `/tmp/workflow` 
in the directory field and then click Execute

To run, navigate to homepage at `http://127.0.0.1:8000/` and
click the workflow on the left side. Then click Run

### Upload via the Python API

We will use python requests to demonstrate this

```python
import requests

r = requests.post('http://127.0.0.1:8000/upload?directory=/tmp/workflow')
print(r)
print(r.text)
```

## Proposal

To make things more uniform I suggest the following routes

* `http://127.0.0.1:8000/upload?directory=/tmp/workflow`
* `http://127.0.0.1:8000/upload?tar=/tmp/workflow.tar`
* `http://127.0.0.1:8000/upload?tgz=/tmp/workflow.tar.gz`
* `http://127.0.0.1:8000/upload?tgz=/tmp/workflow.tgz`
* `http://127.0.0.1:8000/upload?xz=/tmp/workflow.xz`
* `http://127.0.0.1:8000/upload?yaml=/tmp/workflow.yaml`

* `http://127.0.0.1:8000/upload?script=/tmp/workflow/a.sh`
* `http://127.0.0.1:8000/upload?script=/tmp/workflow/b.py`
* `http://127.0.0.1:8000/upload?script=/tmp/workflow/c.ipynb`

Only one of them can be used at a time.
