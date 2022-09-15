# Workflow Quickstart Menu

It assumes that you have cloudmesh cc installed 

```bash
pip install cloudmesh-cc
```

We also assume you start the service with

```bash
cms cc start --reload
```

## Upload a workflow embedded in a tar file

```bash
mkdir /tmp/workflow
cp tests/workflows/workflow.yaml /tmp/workflow
cp tests/workflow-sh/*.sh /tmp/workflow
tar -cf workflow.tar /tmp/workflow/*
```

## Use API

Navigate to `http://127.0.0.1:8000/docs` and use
the POST Upload Workflow method. Click `Try it out`
and then `Add string item` then browse for
`/tmp/workflow/workflow.tar` and then click Execute

## Run workflow

Navigate to homepage at `http://127.0.0.1:8000/` and
click the workflow on the left side. Then click Run