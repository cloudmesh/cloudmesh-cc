# Guide to cloudmesh cc Workflow

The Workflow class in cloudmesh-cc allows the creation of workflows, which are
compilations of jobs to be run on nodes. These workflows report information on
the status of jobs as they are run, whether locally or remotely. These jobs
can be customized to run as bash scripts, Python scripts, Jupyter notebooks,
or Slurm scripts.

Users can utilize the Workflow class in three different ways: through the
command line interface, through a locally hosted web interface with FastAPI,
or with REST API.

The usefulness of such Workflow class includes the ability to upload
a mixture of different types of jobs together, including local and remote;
Slurm and shell; Windows and Unix; and so on. It also allows for a more
efficient job execution as opposed to manually inputting commands repeatedly
at a terminal. For example, a one-time specification inside a YAML
configuration file automatically sets up log generation, fetches the log,
reports progress, resets results on rerun, and other helpful features. 

In this documentation, we describe the installation and methods for this class,
as well as the four different ways to interface the class: through command line
interface, Python, browser GUI through local FastAPI server, or REST
interface through local FastAPI server.

## Requirements

Downloading the code is relatively simple. We leverage the cloudmesh-installer
to locally install the cloudmesh suite of repositories.

```bash
mkdir ~/cm
cd ~/cm
pip install cloudmesh-installer -U
cloudmesh-installer get cc
```

### Windows

Git Bash and Graphviz must be installed. The user can use Chocolatey run as
an administrator for convenience:

```bash
choco install git.install --params "/GitAndUnixToolsOnPath \
        /Editor:Nano /PseudoConsoleSupport /NoAutoCrlf" -y
choco install graphviz -y
```

### macOS

Graphviz must be installed. The user can use Homebrew for convenience:

```zsh
brew install graphviz
```

### Linux

Graphviz is included in a normal Ubuntu installation, but the user should
install Graphviz if not on the machine with the following command:

```bash
sudo apt install graphviz
```

## A. Use Workflow Class in Python Code

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

## B. Use Browser GUI Through Local FastAPI Web Server

The web server provides a more customizable, easy-to-use interface
for the Workflow class. To start the web server, issue commands:

```bash
cd ~/cm/cloudmesh-cc
cms cc start
```

Then, in a web browser, open the link http://127.0.0.1:8000/

The browser provides an interface to view preexisting workflows
in both a DataTable format and as a graph format. Both views will
update automatically, in a live fashion, as the workflows are run,
reporting live job status and progress.

For a quick and easy example of leveraging this GUI interface,
click on the Example tab in the left-hand sidebar. Then, a
workflow-example will appear underneath Workflows. Click on the
workflow-example and run the workflow by clicking the green Run
button in the top-right. As the workflow runs, the user is able
to click on the Graph button and back to the Table button, as
desired, to view the workflow's progression.

## Details about Workflow Class

The scripts must leverage some format of cloudmesh.progress
to run successfully. Otherwise, the Workflow class cannot tell
if the scripts are done, breaking the functionality.

### Shell and Slurm Scripts

For shell and Slurm scripts `.sh`, the script must contain:

```bash
echo "# cloudmesh status=running progress=1 pid=$$"
```

at the beginning of the script, and

```bash
echo "# cloudmesh status=done progress=100 pid=$$"
```

at the end of the script.

### Python Scripts and Jupyter Notebooks

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

- be written to a filename with the same name as the script 
- begin at progress=1
- and end at progress=100
