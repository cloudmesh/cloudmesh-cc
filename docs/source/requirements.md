# Requirements

The scripts must leverage some format of cloudmesh.progress
to run successfully. Otherwise, the Workflow class cannot tell
if the scripts are done, breaking the functionality.

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

- be written to a filename with the same name as the script 
- begin at progress=1
- and end at progress=100