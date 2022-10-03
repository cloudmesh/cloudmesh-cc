# Python Interface

In Python, we can instantiate an instance of the Workflow class to
create a new Workflow. We supply an arbitrary filename for the workflow and
specify that we are not loading a preexisting one, but creating a new one.

```python
from cloudmesh.cc.workflow import Workflow

w = Workflow(name='workflow-example', load=False)
```

Simply instantiating a workflow will create the necessary runtime
directories located on your computer at 
`~/.cloudmesh/workflow/workflow-example`. Within this directory is a `runtime`
directory, where all the scripts of the workflow must be placed. Compatible
script types include shell scripts `.sh`, Python scripts `.py`, Jupyter
notebooks `.ipynb`, and Slurm scripts `.sh` (`#SBATCH` 
directives are required in the Slurm script).

We can utilize some scripts that are already available in the repository for
our workflow-example. We will now use cloudmesh Shell for path expansion and
for copying the scripts.

```python
from cloudmesh.common.Shell import Shell
from pathlib import Path
import os

cloudmesh_cc_dir = Path(Shell.map_filename(
    '~/cm/cloudmesh-cc/tests/workflow-example/').path).as_posix()
scripts = [
    "start.sh", "fetch-data.sh", "compute.sh", "analyze.sh", "end.sh"]
for script in scripts:
    Shell.copy(f"{cloudmesh_cc_dir}/{script}", w.runtime_dir)
```

Lastly, we can enable the running of these scripts by adding jobs to the
workflow object. We can also add dependencies to tell the workflow in which
order to run the jobs.

```python
for script in scripts:
    w.add_job(
        name=script, kind='local', label="{name}\nprogress={progress}")
w.add_dependencies(f"analyze.sh,end.sh")
w.add_dependencies(f"compute.sh,analyze.sh")
w.add_dependencies(f"fetch-data.sh,compute.sh")
w.add_dependencies(f"start.sh,fetch-data.sh")
```

To test our workflow, we can run it in topological order with the command:

```python
os.chdir(w.runtime_dir)
os.chdir('..')
w.run_topo(show=True)
```

The workflow will now run the jobs in a topological order and show the
progress of the jobs in your web browser.

To instead load a YAML file for the configuration of the workflow,
use the `filename=` parameter of the instantiation of the workflow.
The supplied parameter should be a filepath that points to the location
of the YAML, and `load=` should be `True`.

The following is the workflow-example configuration in YAML format.

```bash
workflow:
  nodes:
    start.sh:
       name: start.sh
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: start.sh
    fetch-data.sh:
       name: fetch-data.sh
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: fetch-data.sh
   compute.sh:
       name: compute.sh
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: compute.sh
   analyze.sh:
       name: analyze.sh
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: analyze.sh
   end.sh:
       name: end.sh
       user: gregor
       host: localhost
       kind: local
       status: ready
       label: '{name}\nprogress={progress}'
       script: end.sh
  dependencies:
    - start.sh,fetch-data.sh,compute.sh,analyze.sh,end.sh
```

The different options for kind include local, ssh, slurm, and wsl.
The filetype, e.g. `.sh` or `.py`, is automatically inferred from the
script.
