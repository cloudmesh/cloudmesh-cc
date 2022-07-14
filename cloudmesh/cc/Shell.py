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
    def fake_browser(cls, filename=None, engine='python -m webbrowser -t', browser=None):
        _filename = Shell_path.map_filename(filename)
        if _filename.path.startswith('http'):
            result = requests.get(_filename.path)
            return result.text
        else:
            os.path.exists(_filename.path)
            result = readfile(_filename.path)
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
        result = dotdict()

        result.user = os.path.basename(os.environ["HOME"])
        result.host = "localhost"
        result.protocol = "localhost"

        if _name.startswith("http"):
            result.path = _name
            result.protocol = _name.split(':')[0]
        elif _name.startswith("wsl:"):
            result.path = _name.replace("wsl:", "")\
                .replace("~",f"/mnt/c/Users/{result.user}")\
                .replace("home",f"Users/{result.user}")
            result.protocol = "cp"
            result.host = "wsl"
        elif _name.startswith("scp:"):
            # scp source destination
            try:
                result.scp, userhost, result.path = _name.split(":")
                result.user, result.host = userhost.split("@")
                result.protocol = "scp"
            except:
                Console.error("The format of the name is not supported: {name}")
        elif _name.startswith("rsync:"):
            try:
                result.scp, userhost, result.path = _name.split(":")
                result.user, result.host = userhost.split("@")
                result.protocol = "rsync"
            except:
                Console.error("The format of the name is not supported: {name}")
        elif _name.startswith(".") or _name.startswith("~"):
            result.path = path_expand(_name)
        elif _name[1] == ":":
            drive, path = _name.split(":", 1)
            result.path = drive + ":" + path_expand(path)
            result.path = result.path.replace("/", "\\")
        else:
            result.path = path_expand(_name)

        return result


    def path_abs(text, slashreplace=True):
        """ returns a string with expanded variable.

        :param text: the path to be expanded, which can include ~ and environment variables
        :param text: string

        """
        result = os.path.expandvars(os.path.expanduser(text))

        if not result.startswith("./"):
            result = "./" + result

        if result.startswith("./"):
            result = result.replace(".", os.getcwd(), 1)

        # if is_gitbash() or is_cmd_exe():
        #     if slashreplace:
        #         result = result.replace("/", "\\")

        return result

    @classmethod
    # @NotImplementedInWindows
    def head(cls, *args):
        """
        executes head with the given arguments
        :param args:
        :return:
        """
        pass