from cloudmesh.common.variables import Variables
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
