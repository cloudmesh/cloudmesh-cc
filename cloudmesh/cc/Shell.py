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
        print('a', filename)
        _filename = Shell_path.map_filename(filename)
        print('b', _filename)
        if _filename.path.startswith('http'):
            result = requests.get(_filename.path)
            print(result.text)
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
                protocol = source_map.protocol if not "cp" else dest_map.protocol
                command = f"{protocol} {source_map.path} {dest_map.path}"
                os.system(command)


    @staticmethod
    def map_filename(name):
        _name = str(name)
        result = dotdict()

        print('bbb', _name)

        # regular
        result.path = _name
        result.protocol = "cp"
        result.user = os.path.basename(os.environ["HOME"])
        result.host = "localhost"

        if _name.startswith("http"):
            result.path = _name
            result.protocol = _name.split(':')[0]
            result.user = os.path.basename(os.environ["HOME"])
            result.host = "localhost"
        elif _name.startswith("wsl:"):
            if os_is_windows():
                user = os.environ["USERNAME"]
                result.path = _name.replace("wsl:", f"/mnt/c/Users/{user}/").replace("~","")
                result.protocol = "cp"
                result.user = user
                result.host = "wsl"
            else:
                Console.error("wsl is only compatible with Windows")
        elif _name.startswith("scp:"):
            # scp source destination
            if '@' in _name:
                result.scp, userhost, result.path = _name.split(":")
                result.user, result.host = userhost.split("@")
                result.protocol = "scp"
                result.path=f"{result.user}@{result.host}:{result.path}"
            else:
                Console.error("format of scp command is not correct")
        elif _name.startswith("rsync:"):
            # rsync -a
            if '@' in _name:
                result.scp, userhost, result.path = _name.split(":")
                result.user, result.host = userhost.split("@")
                result.protocol = "rsync -a"
                f"{result.user}@{result.host}:{result.path}"
            else:
                Console.error("format of rsync command is not correct")

        elif _name.startswith("."):
            result.path = path_expand(_name)
            result.protocol = "localhost"
            result.user = os.path.basename(os.environ["HOME"])
            result.host = "localhost"
        elif _name.startswith("~"):
            result.path = path_expand(_name)
            result.protocol = "localhost"
            result.user = os.path.basename(os.environ["HOME"])
            result.host = "localhost"
        else:
            result.path = path_expand(f'./{_name}')
            result.protocol = "localhost"
            result.user = os.path.basename(os.environ["HOME"])
            result.host = "localhost"
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