# MNIST Workflow

For this example we use UVA's Rivanna machine. Please adopt 
it to your HPC machine.

We can test Rivanna's GPUs and benchmark
their runtimes for running several MNIST
Python programs. These programs include
machine learning processing, convolutional
neural network, long short-term memory,
recurrent neural network, and others.
The programs can be found at
<https://github.com/cybertraining-dsc/reu2022/tree/main/code/deeplearning/mnist>

To run the MNIST remote workflow on
Rivanna, first ensure that your UVA computing
ID is set with the following command:

```bash
cms set username=XXXXXX
```
where the X's are substituted with your computing ID.

Then, issue commands:

```bash
cd ~/cm/cloudmesh-cc
pytest -v -x --capture=no examples/example_run_mnist_workflow_exec.py
```

This program uses SLURM and a shell script to
iterate through the available GPUs on Rivanna,
which are V100, A100, K80, P100, and RTX2080.

On a successful run, the output will be similar to
the following:

```
+---------+----------+---------+---------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------+
| Name    | Status   |    Time |     Sum | Start               | tag   | msg   | Node        | User   | OS    | Version                             |
|---------+----------+---------+---------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------|
| v100    | ok       | 138.087 | 138.087 | 2022-09-29 18:15:45 |       |       | udc-ba34-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| a100    | ok       | 106.046 | 106.046 | 2022-09-29 18:18:05 |       |       | udc-ba34-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| k80     | ok       | 171.057 | 171.057 | 2022-09-29 18:19:52 |       |       | udc-ba34-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| p100    | ok       | 202.055 | 202.055 | 2022-09-29 18:22:44 |       |       | udc-ba34-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| rtx2080 | ok       | 138.048 | 138.048 | 2022-09-29 18:26:07 |       |       | udc-ba34-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
+---------+----------+---------+---------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------+
```
