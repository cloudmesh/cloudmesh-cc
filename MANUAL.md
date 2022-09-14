# Workflow Quickstart Menu

It assumes that you have cloudmesh cc installed 

```bash
pip install cloudmehs-cc
```

We also assume you start the service with

```bash
cms cc start --reload
```

## Upload a workflow embedded in a tar file

```bash
mkdir /tmp/workflow
cp  tests/workflows/workflow.yaml /tmp/workflow
cp  tests/workflow-sh/*.sh /tmp/workflow
cd tar
```