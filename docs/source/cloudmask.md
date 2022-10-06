# Cloudmask Workflow

Cloudmesh cc comes with an example workflow
that runs Cloudmask, which is a program that
develops a model to classify sections of satellite 
images. Information regarding Cloudmask can be found at
<https://github.com/laszewsk/mlcommons/tree/main/benchmarks/cloudmask#readme>

## Running the Cloudmask Workflow on Rivanna

To execute the workflow on UVA's HPC supercomputer,
Rivanna, first ensure that your UVA Computing ID
is set with the following command, replacing the
X's with your ID:

```bash
me@mycomputer $ cms set username=XXXXXX
```

Then, connect to the UVA Anywhere VPN and then
download the satellite data into your [scratch](https://www.rc.virginia.edu/userinfo/storage/non-sensitive-data/#scratch)
directory on Rivanna:

```bash
me@mycomputer $ cms vpn connect
me@mycomputer $ ssh rivanna
rivanna $ cd /scratch/$USER
rivanna $ git clone https://github.com/laszewsk/mlcommons.git
rivanna $ cd mlcommons/benchmarks/cloudmask/target/rivanna
rivanna $ make data
# downloading the data will take a while.
rivanna $ exit
```

Next, clone the `mlcommons` repository on your local machine
and run the workflow:

```bash
me@mycomputer $ cd ~/cm
me@mycomputer $ git clone https://github.com/laszewsk/mlcommons.git
me@mycomputer $ cd mlcommons
me@mycomputer $ pytest -v -x --capture=no benchmarks/cloudmask/target/rivanna/run_cloudmask_workflow.py
```

The workflow iterates through the five GPUs available
on Rivanna— A100, V100, P100, RTX2080, and K80— and 
runs the program three times on each GPU. Each run 
trains the model with 10, 30, and 50 epochs for
benchmarking.

Upon completing a run, the logs and benchmarks of the
program can be found in the target folder:

```bash
me@mycomputer $ ssh rivanna
rivanna $ cd /scratch/$USER/mlcommons/benchmarks/cloudmask/target
```

Additionally, the generated `.h5` model file can be found in the
home directory:

```bash
rivanna $ cd ~/sciml_bench/outputs/slstr_cloud/
```

The program may take a while to run if the resources
on Rivanna are being used by other jobs.