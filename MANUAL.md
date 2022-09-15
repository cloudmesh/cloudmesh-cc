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

### Uploald via `curl`

TBD

### Uploald via /docs

```bash
mkdir -p /tmp/workflow
cp tests/workflows/workflow.yaml /tmp/workflow
cp tests/workflow-sh/*.sh /tmp/workflow
tar -C /tmp/workflow -cf workflow.tar .
```

Navigate to `http://127.0.0.1:8000/docs` and use
the POST Upload Workflow Tar method

`http://127.0.0.1:8000/docs/upload_tar`

Please, click `Try it out`
and then `Add string item` then browse for
`/tmp/workflow/workflow.tar` and then click Execute

Navigate to homepage at `http://127.0.0.1:8000/` and
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

### Uploald via `curl`

A workflow can be uploades easily with a curl command from the commandline.
On the commandline execute:

'''bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload_dir?dir_path=/tmp/workflow' \
  -H 'accept: application/json' \
  -d ''
'''

TODO: on windows it also should work with / and not \ We make explicit note here
when using a drive we do /c/ ....

### Uploald via /docs


Navigate to `http://127.0.0.1:8000/docs` and use
the POST Upload Workflow Dir method

`http://127.0.0.1:8000/docs/upload_dir`

Click `Try it out`
and then enter `/tmp/workflow` in the box and then
click Execute

Navigate to homepage at `http://127.0.0.1:8000/` and
click the workflow on the left side. Then click Run

### Upload via the Python API

We will use python requests to demonstarte this

```python
import requests

r = requests.post('http://127.0.0.1:8000/upload_dir?dir_path=/tmp/workflow')
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
