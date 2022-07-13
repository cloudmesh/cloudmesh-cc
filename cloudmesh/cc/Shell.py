import os

from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.systeminfo import os_is_windows


class Shell_path:
    @staticmethod
    def map_filename(name):
        _name = str(name)
        dest = dotdict()

        if _name.startswith("wsl:"):
            if os_is_windows():
                user = os.environ["USERNAME"]
                dest.path = _name.replace("wsl:", f"/mnt/c/Users/{user}/")
                dest.protocol = "wsl"
                dest.user = user
                dest.host = "wsl"
            else:
                Console.error("wsl is only compatible with Windows")
        if _name.startswith("scp:"):
            if '@' in _name:
                dest.scp, userhost, dest.path = _name.split(":")
                dest.user, dest.host = userhost.split("@")
                dest.protocol = "scp"
            else:
                Console.error("format is not correct")
        return _name, dest