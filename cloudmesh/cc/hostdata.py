"""Cloudmesh cc host data."""
from cloudmesh.common.Shell import Shell
import os
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from os.path import expanduser
import shutil


class Host:

    def __int__(self, location):
        self.user = None
        self.host = None
        self.path = None
        self.location = None
        self.name = None
        self.directory = None
        self.set(location)

    def set(self, location):
        """
        location has the form username@host:directory

            abc@localhost:~/cm/cloudmesh-cc/test/dir
            xyz1jk@rivanna.hpc.virginia.edu:~/cm/cloudmesh-cc/test/dir

        Args:
            location (str):

        Returns:
            list of user, host, location

        """
        self.user, rest = location.split("@")
        self.host, self.path = rest.split(":")
        if self.host == "localhost":
            self.location = self.path
        else:
            self.location = str(self)

        return self.user, self.host, self.path

    def __str__(self):
        return f"{self.user}@{self.host}:{self.path}"

    def mkdir(self, directory):
        if self.host in ['localhost', "127.0.0.1"]:
            Shell.mkdir(directory)
        else:
            Shell.ssh(f"{self.user}@{self.host} mkdir -p {self.path}")

    def scp(self, source, destination):
        if self.host in ['localhost', "127.0.0.1"]:
            destination = shutil.copytree(source, destination)
        else:
            self.mkdir(self.path)
            Shell.scp(source, destination)

    def sync(self, source, destination):
        if self.host in ['localhost', "127.0.0.1"]:
            destination = shutil.copytree(source, destination)
        else:
            self.mkdir(self.path)
            os.system(f"rsync -a {source} {self.user}@{self.host}:{destination}")


"""
Step1 

localhost:
  ~/tmp/a/1.txt
  ~/tmp/a/2.txt
  ~/tmp/b/3.txt
  ~/tmp/b/4.txt

Step2
  
rivanna:
  nothing  

step 3
cms data upload ~/tmp/a/1.txt
cms data list rivanna:~/tmp

cms data upload ~/tmp/b/3.txt
cms data list rivanna:~/tmp

cms data upload ~/tmp/a
cms data list rivanna:~/tmp

cms data upload ~/tmp
cms data list rivanna:~/tmp

output
rivanna:
  ~/tmp/a/1.txt
  ~/tmp/a/2.txt
  ~/tmp/b/3.txt
  ~/tmp/b/4.txt


"""


class Data:
    """
    local and remote have the form

    username@host:directory

    """

    def __init__(self, local=None, remote=None):
        """

        Args:
            local ():
            remote ():
        """
        self.remote_host = None
        self.local_host = None
        self.set(loacl=local, remote=remote)
        if self.remote_host is None:
            Console.error("Remote Host not set")
        if self.local_host is None:
            Console.error("Remote Host not set")

    def set(self, local=None, remote=None):
        """

        Args:
            local ():
            remote ():

        Returns:

        """
        self.local_host = Host(local)
        self.remote_host = Host(remote)

    def mkdir(self, directory=None):
        """

        Args:
            directory ():

        Returns:

        """
        if directory is None:
            raise ValueError("creating directory with value None is not supported")
        try:
            self.remote_host.mkdir(directory)
        except Exception as e:
            print(e)
            raise ValueError(f"can not create directory on {self.remote_host}")

    def upload(self, name=None):
        """

        Args:
            name ():

        Returns:

        """
        # get cwd directory if name is None
        if name is None:
            name = "."

        home_dir = expanduser("~")
        local_location = path_expand(name)
        remote_location = local_location.replace(home_dir, "")

        if os.path.isdir(name):
            remote_dir = remote_location
            self.remote_host.mkdir(remote_dir)

        elif os.path.isfile(name):
            filename = os.path.basename(remote_location)
            remote_dir = os.path.dirname(remote_location)
            remote_file = remote_location
            self.remote_host.mkdir(remote_dir)
            self.remote_host.scp(name, remote_file)

    def delete(self, name=None):
        """

        Args:
            name ():

        Returns:

        """
        raise NotImplementedError(" ON PURPOSE NOT IMPLEMENTED AS LOGIC NEEDS TO BE WORKED OUT ")
        if name is not None:
            self.name = name
        self.directory = os.getcwd()
        print(self.directory)
        os.remove(f'{self.remote}/{self.name}')

    def update(self, name=None):
        """

        Args:
            name ():

        Returns:

        """
        # deleting is needed in case the new dire has not all files as the old one has
        # I would actually prefer to use rsync
        self.delete(name)
        self.upload(name)
