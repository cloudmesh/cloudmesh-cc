import os
import sys
import torch
import textwrap
import socket
import cpuinfo
from cloudmesh.common.util import banner
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.variables import Variables
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import progress
import time

StopWatch.progress(0)

dryrun = False

exec = "python"
exec = "papermill"
exec = "sbatch"

v = Variables()

user = v["user"] or Shell.sys_user().replace(' ', '_').replace('-', '_')
host = v["host"] or socket.gethostname().replace(' ', '_').replace('-', '_')
gpu = v["gpu"]
cpu = v["cpu"]
device = v["device"]

error = False

if user is None:
    Console.error("user not set")
    error = True

if host is None:
    Console.error("host not set")
    error = True

# if cpu is None:
#     Console.error("cpu not set")
#     error = True
#
# if gpu is None:
#     Console.error("gpu not set")
#     error = True
#
# if device is None:
#     Console.error("device not set")
#     error = True

if error:
    sys.exit()

StopWatch.progress(5)

# scripts = textwrap.dedent("""
# mlp_mnist
# mnist_autoencoder
# mnist_cnn
# mnist_lstm
# mnist_mlp_with_lstm
# mnist_rnn
# mnist_with_distributed_training
# mnist_with_pytorch
# """).strip().splitlines()

scripts = textwrap.dedent("""
mlp_mnist
""").strip().splitlines()

# mnist_cnn
# mnist_lstm
# mnist_mlp_with_lstm
# mnist_rnn
# mnist_with_distributed_training
# mnist_with_pytorch

host = 'rivanna'

#if gpu is None:
gpu = ['v100', 'a100', 'k80', 'p100']
#gpu = ['a100']
#else:
#    gpu = v['gpu'].split(',')
path = Shell.map_filename('~/cm/cloudmesh-cc/tests/mnist').path
os.chdir(path)
for card in gpu:
    tag = f"{host}-{user}-{cpu}-{card}"
    for script in scripts:
        if exec == "papermill":
            output = f"{script}-output"
            command = f"{exec} {script}.ipynb {output}.ipynb"
        elif exec == 'sbatch':
            command = f"{exec} --wait --gres=gpu:{card}:1 {script}.sh"
        banner(command)
        if not dryrun:
            os.chdir(path)
            banner(command)
            try:
                Shell.run(f'cms set currentgpu={card}')
                StopWatch.start(f'{card}')
                Shell.run(command)
                StopWatch.stop(f'{card}')
                Shell.run(f'cms set delete currentgpu')
            except Exception as e:
                print(e.output)

    for script in scripts:

        command = f'cat {script}.log'
        r = Shell.run(command)
        while 'progress=100' not in str(r):
            time.sleep(2)
            r = Shell.run(command)
            continue


    StopWatch.benchmark(sysinfo=False, node=host, user=user)

StopWatch.benchmark(sysinfo=False, filename=f"all-mnist.log")

StopWatch.progress(100)


