# Specifying Workflows

Users of cloudmesh cc must follow a certain
configuration style to best specify how a
workflow should be run. Customization options
include specifying the job types, the order of
how the jobs should be run, and the portrayal
of the graph.

## Workflow YAML format

A workflow yaml file with three Shell script
jobs `a`, `b`, and `c` is as follows:

```bash
workflow:
  nodes:
    a:
       name: a
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: test-a.sh
    b:
       name: b
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: test-b.sh
    c:
      name: c
      user: gregor
      host: localhost
      kind: local
      status: ready
      label: '{name}\nprogress={progress}'
      script: test-c.sh
  dependencies:
    - a,b,c
```

## Example Workflows

Sample yaml files can be found at the following link:

<https://github.com/cloudmesh/cloudmesh-cc/blob/main/tests/workflow-example/workflow-example.yaml>

## Defining nodes in the workflow

### Defining labels for the workflow

These variables must be in curly braces.

* `progress`
* time
  * `%now` now
  * `now.%m/%d/%Y, %H:%M:%S` now in particular format
  * `%tc` created
  * `%tm` modified
  * `%dt0` time since start of first node
  * `%dt` time since start of current node
    (duration once finished)
  * `name`
  * `label`
  * `host`

## Defining format for timestamp labels

## Defining graphviz shapes and styles

https://graphviz.org/doc/info/shapes.html

https://graphviz.org/docs/attr-types/style/

```text
workflow:
  nodes:
    start:
      label: 'start\nWorkflow Started={t0.}\nElapsed={dt0.}\nCreated={created.%Y/%m/%d, %H--%M--%S}'
      kind: local
      user: grey
      host: local
      status: ready
      exec: 'echo hello'
      name: start
      shape: box
      style: ''
```
  

## Defining dependencies in the workflow

Dependencies are specified in the order which jobs should be
run, from left to right. They are listed under the workflow
in the yaml file.

```bash
workflow:
  nodes:
    a:
       name: a
    b:
       name: b
    c:
       name: c
  dependencies:
    - a,b,c
```

## Reporting Progress

When running scripts/jobs inside a workflow, the scripts must 
leverage some format of cloudmesh.progress to run successfully. 
Otherwise, the Workflow class cannot tell
if the scripts are done, breaking the progress functionality.

The examples that are provided with cloudmesh-cc are
already augmented with cloudmesh.progress. Thus, if a user is
running self-made jobs and workflows, they must adhere to the
guidelines as follows.

## Shell and Slurm Scripts

For shell and Slurm scripts `.sh`, the script must contain:

```bash
echo "# cloudmesh status=running progress=1 pid=$$"
```

at the beginning of the script, and

```bash
echo "# cloudmesh status=done progress=100 pid=$$"
```

at the end of the script.

## Python Scripts and Jupyter Notebooks

For Python scripts `.py` and Jupyter notebooks `.ipynb`,
the script must contain an import module from 
cloudmesh.common and calls to the progress function.

py_script.py

```bash
from cloudmesh.common.StopWatch import progress
from cloudmesh.common.Shell import Shell
filename = Shell.map_filename('./py_script.log').path
progress(progress=1, filename=filename)

# your script does what you want it to do here...

progress(progress=100, filename=filename)
```

The statements do not need to be at the absolute beginning
or end of the script, but the progress must:

- be written to a filename with the same name as the script,
ending in `.log`
- begin at progress=1
- and end at progress=100