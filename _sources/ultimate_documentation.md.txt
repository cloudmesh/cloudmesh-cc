# Guide to cloudmesh cc Workflow

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



## A. Use Workflow Class in Python Code


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
