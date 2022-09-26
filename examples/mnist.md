# Running MNIST Workflow on Rivanna

We can test Rivanna's GPUs and benchmark
their runtimes for running several MNIST
Python programs. These programs include
machine learning processing, convolutional
neural network, long short-term memory,
recurrent neural network, and others.

To run the MNIST remote workflow on
Rivanna, first ensure that your UVA computing
ID is set with `cms set username=XXXXXX`, where
the X's are substituted with your computing ID.

Then, stand in `cloudmesh-cc` and issue command
`pytest -v -x --capture=no examples/example_run_mnist_workflow_exec.py`

This program uses SLURM and a shell script to
iterate through the available GPUs on Rivanna,
which are V100, A100, K80, and P100.

On a successful run, the output will be similar to
the following:

```bash
| Name       | Status   |    Time |      Sum | Start               | tag   | msg   | Node        | User   | OS    | Version                             |
|------------+----------+---------+----------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------|
| v100-total | ok       | 330.095 |  330.095 | 2022-09-25 18:51:45 |       |       | udc-ba35-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| mlp_mnist  | ok       | 426.09  | 1736.42  | 2022-09-25 19:13:35 |       |       | udc-ba35-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| a100-total | ok       | 266.099 |  266.099 | 2022-09-25 18:57:15 |       |       | udc-ba35-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| k80-total  | ok       | 714.186 |  714.186 | 2022-09-25 19:01:41 |       |       | udc-ba35-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
| p100-total | ok       | 426.106 |  426.106 | 2022-09-25 19:13:35 |       |       | udc-ba35-36 | XXXXXX | Linux | #1 SMP Wed Feb 23 16:47:03 UTC 2022 |
+------------+----------+---------+----------+---------------------+-------+-------+-------------+--------+-------+-------------------------------------+
```