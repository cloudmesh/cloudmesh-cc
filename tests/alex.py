import os
from pathlib import Path
from cloudmesh.common.Shell import Shell

name = 'run'

command = f'cd ~/c/Users/abeck'

directory = os.system(command)

print(directory)