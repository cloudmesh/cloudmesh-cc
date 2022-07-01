import os
from pathlib import Path

import cloudmesh
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand

# path = path_expand(f'/c/Users/abeck/experiment/run')
# try:
#     command = Shell.run(f'wsl cd \mnt{path}')
# except Exception as e:
#     print(e.output)

try:
    command = Shell.run(f'wsl -e cd /home/abeck && pwd')
    print(command)
except Exception as e:
    print('c')

command = Shell.run(f'wsl -e cd /home/abeck && pwd')
print(command)

# name = 'run'
# dir = path_expand('~')
# command = f'cd {dir} && pwd'
# directory = Shell.run(command)
# except Exception as e:
#     print(e.output)
#
# print(directory)