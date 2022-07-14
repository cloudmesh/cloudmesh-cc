import os
import shutil

from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.systeminfo import os_is_windows, os_is_linux, os_is_mac
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.Shell import Shell

import webbrowser
import requests


class Shell_path:

    @staticmethod
    def open(filename=None, program=None):
        if not os.path.isabs(filename):
            filename = path_expand(filename)

        if os_is_linux():
            r = Shell.run(f"gopen {filename}")
        if os_is_mac():
            command = f'open {filename}'
            if program:
                command += f' -a "{program}"'
            r = Shell.run(command)
        if os_is_windows():
            r = Shell.run(f"start {filename}")

        return r

    @staticmethod
    def browser(filename=None):
        """
        :param filename:
        :return:
        """
        if not os.path.isabs(filename) and 'http' not in filename:
            filename = Shell_path.map_filename(filename).path
        webbrowser.open(filename, new=2)

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
        pwd = os.getcwd()

        _name = str(name)
        result = dotdict()

        result.user = os.path.basename(os.environ["HOME"])
        result.host = "localhost"
        result.protocol = "localhost"

        if _name.startswith("http"):
            result.path = _name
            result.protocol = _name.split(':',1)[0]
        elif _name.startswith("wsl:"):
            result.path = _name.replace("wsl:", "")
            # Abbreviations: replace ~ with home dir and ./ + / with pwd
            if result.path.startswith("~"):
                if os_is_linux():
                    result.path = result.path.replace("~",f"/mnt/c/home/{result.user}")
                else:
                    result.path = result.path.replace("~",f"/mnt/c/Users/{result.user}")
            elif not result.path.startswith("/"):
                if os_is_windows():
                    pwd = pwd.replace("C:","/mnt/c").replace("\\","/")
                result.path = pwd + "/" + result.path.replace("./","")
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
            if os_is_windows():
                result.path = path_expand(path)
            else:
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
    def head(cls, filename=None, lines=10):
        """
        executes head with the given arguments
        :param args:
        :return:
        """
        filename = cls.map_filename(filename).path
        r = Shell.run(f'head -n {lines} {filename}')
        return r

    @classmethod
    def ping(cls, host=None, count=1):
        """
        execute ping
        :param host: the host to ping
        :param count: the number of pings
        :return:
        """
        r = None
        option = '-n' if os_is_windows() else '-c'
        parameters = "{option} {count} {host}".format(option=option,
                                                      count=count,
                                                      host=host)
        r = Shell.run(f'ping {parameters}')
        if r is None:
            Console.error("ping is not installed")
        return r

    @classmethod
    def tail(cls, filename=None, lines=10):
        """
        executes tail with the given arguments
        :param args:
        :return:
        """
        filename = cls.map_filename(filename).path
        r = Shell.run(f'tail -n {lines} {filename}')
        return r

    @classmethod
    def mkdir(cls, directory):
        """
        creates a directory with all its parents in ots name
        :param directory: the path of the directory
        :return:
        """
        directory = cls.map_filename(directory).path
        try:
            os.makedirs(directory)
            return True
        except OSError as e:
            return False
        #

        '''EEXIST (errno 17) occurs under two conditions when the path exists:
        - it is a file
        - it is a directory

        if it is a file, this is a valid error, otherwise, all
        is fine.
           if e.errno == errno.EEXIST and os.path.isdir(directory):
               pass
           else:
               raise'''