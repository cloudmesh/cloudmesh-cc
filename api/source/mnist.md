# MNIST Workflows

For this example we use UVA's Rivanna machine. Please adopt 
it to your HPC machine.

We can test Rivanna's GPUs and benchmark
their runtimes for running several MNIST
Python programs. These programs include
machine learning processing, convolutional
neural network, long short-term memory,
recurrent neural network, and others.

To run the MNIST remote workflow on
Rivanna, first ensure that your UVA computing
ID is set with 

```bash
cms set username=XXXXXX
```
where  the X's are substituted with your computing ID.

Then, issue commands:

```bash
cd ~/cm/cloudmesh-cc
pytest -v -x --capture=no examples/example_run_mnist_workflow_exec.py
```

This program uses SLURM and a shell script to
iterate through the available GPUs on Rivanna,
which are V100, A100, K80, and P100.

On a successful run, the output will be similar to
the following:

```
+--------+----------+----------+----------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------+
| Name   | Status   |     Time |      Sum | Start               | tag   | msg   | Node        | User   | OS    | Version                             |
|--------+----------+----------+----------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------|
| v100   | ok       |  298.068 |  298.068 | 2022-09-26 22:56:24 |       |       | udc-ba36-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| a100   | ok       | 1226.18  | 1226.18  | 2022-09-26 23:07:56 |       |       | udc-ba36-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| k80    | ok       |  714.123 |  714.123 | 2022-09-26 23:28:24 |       |       | udc-ba36-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| p100   | ok       |  458.094 |  458.094 | 2022-09-26 23:40:19 |       |       | udc-ba36-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
+--------+----------+----------+----------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------+
```
