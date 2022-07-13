import os
import shutil

from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.systeminfo import os_is_windows, os_is_linux, os_is_mac
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile

import webbrowser
import requests


class Shell_path:

    @staticmethod
    def browser(filename=None, engine='python -m webbrowser -t',
                browser=None):
        """
        :param filename:
        :param engine:
        :param browser:
        :return:
        """
        if not os.path.isabs(filename) and 'http' not in filename:
            filename = path_expand(filename)

        if ".svg" in filename:
            if browser:
                try:
                    webbrowser.get(browser).open(filename, new=2)
                except Exception as e:
                    Console.error('Specified browser not available.')
            else:
                webbrowser.open(filename, new=2)
        else:
            if 'file:' not in filename and 'http' not in filename:
                command = f"{engine} file:///{filename}"
            else:
                webbrowser.open(filename, new=2)
        #print(command)
        #os.system(command)
        return None

    @classmethod
    def fake_browser(filename=None, engine='python -m webbrowser -t', browser=None):
        print('a', filename)
        _filename = Shell_path.map_filename(filename)
        print('b')
        if _filename.path.startswith('http'):
            result = requests.get(_filename)
            print(result.text)
            return result.text
        else:
            os.path.exists(_filename)
            result = readfile(_filename)
            return result

    @classmethod
    def copy(cls, source, destination, expand=False):
        if expand:
            s = path_expand(source)
            d = path_expand(destination)
            shutil.copy2(s, d)
        else:
            source_map = Shell_path.map_filename(source)
            dest_map = Shell_path.map_filename(destination)
            s = source_map.path
            d = dest_map.path

            if source_map.host == "localhost" or source.map.host == "wsl":
                shutil.copy2(s, d)
            else:
                pass
                # protocol = source_map.protocol if not "cp" else dest_map.protocol
                # command = f"{protocol} {source_map.path} {dest_map.path}"
                # os.system(command)


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
                dest.path = _name.replace("wsl:", f"/mnt/c/Users/{user}/").replace("~","")
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

    @classmethod
    # @NotImplementedInWindows
    def head(cls, *args):
        """
        executes head with the given arguments
        :param args:
        :return:
        """
        pass