import os
import shutil

from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Shell


class Shell_path:

    @classmethod
    def copy(cls, source, destination, expand=False):
        if os_is_windows():
            user = os.environ["USERNAME"]
        else:
            user = os.environ["USER"]

        if expand:
            s = path_expand(source)
            d = path_expand(destination)
            shutil.copy2(s, d)
        else:
            source_map = source.map_filename()
            dest_map = destination.map_filename()
            s = source_map.path
            d = dest_map.path

            if source_map.host == "localhost" or source.map.host == "wsl":
                shutil.copy2(s, d)
            else:
                pass


    @staticmethod
    def map_filename(name):
        _name = str(name)
        dest = dotdict()

        # regular
        dest.path = _name
        dest.protocol = "cp"
        dest.user = os.system('for /F %i in ("%userprofile%") do @echo %~ni') if os_is_windows() else os.environ["USER"]
        dest.host = "localhost"

        if _name.startswith("wsl:"):
            if os_is_windows():
                user = os.environ["USERNAME"]
                dest.path = _name.replace("wsl:", f"/mnt/c/Users/{user}/")
                dest.protocol = "cp"
                dest.user = user
                dest.host = "wsl"
            else:
                Console.error("wsl is only compatible with Windows")
        if _name.startswith("scp:"):
            # scp source destination
            if '@' in _name:
                dest.scp, userhost, dest.path = _name.split(":")
                dest.user, dest.host = userhost.split("@")
                dest.protocol = "scp"
            else:
                Console.error("format of scp command is not correct")
        if _name.startswith("rsync:"):
            # rsync -a
            if '@' in _name:
                dest.scp, userhost, dest.path = _name.split(":")
                dest.user, dest.host = userhost.split("@")
                dest.protocol = "rsync -a"
            else:
                Console.error("format of rsync command is not correct")
        return dest
