from cloudmesh.common.variables import Variables
from cloudmesh.common.Shell import Shell
import os

def set_host_user():
    variables = Variables()
    if "host" not in variables:
        host = "rivanna.hpc.virginia.edu"
    else:
        host = variables["host"]

    if "username" in variables:
        username = variables["username"]
    else:
        username = os.path.basename(os.environ["HOME"])

    return host, username

def create_dest():
    # os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #
    # Shell.rmdir("dest")
    # Shell.mkdir("dest")
    expanded_path = Shell.map_filename('~/.cloudmesh/workflow').path
    os.chdir(expanded_path)
