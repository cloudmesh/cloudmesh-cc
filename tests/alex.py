import os
from pathlib import Path

import cloudmesh
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand

name = 'run'
dir = path_expand('~')
command = f'cd {dir} && pwd'
directory = Shell.run(command)
except Exception as e:
    print(e.output)

print(directory)