import os
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell

try:
    # sed -i -e 's/\r$//'

    # directory = f"~/experiment/run"
    # bashdir = str(directory)[2:]

    user = os.environ["USERNAME"]
    dir = f'/mnt/c/Users/{user}'
    status = Shell.run(f'wsl sh -c ". ~/.profile && cd {dir} && pwd"')
    print(status)
    # Shell.run(f'wsl nohup sh -c ". ~/.profile && cd {dir} && '
    #           f'./run.sh &"')

    # reset = f'wsl cd //mnt//c//'
    # pwd = f'wsl "pwd"'
    # r = Shell.run(reset)
    # p = Shell.run(pwd)
    # print(r)
    # print(p)
except Exception as e:
    print(e.output)

# try:
#     command = f'start /b wsl -e bash //mnt//c//Users//abeck//experiment//run//run.sh'
#     r = Shell.run(command)
#     print(r)
# except Exception as e:
#     print(e.output)



