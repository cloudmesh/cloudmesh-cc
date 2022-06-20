import os
import shelve
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_windows
import pathlib

#
# convert this to use shelve keep all methods signatures the same
#

class Database:

    def __init__(self, filename=None, debug=False):
        self.debug = debug
        if filename is None:
            filename = "~/.cloudmesh/queue/queues"
        self.fileprefix = filename.replace(".db", "").replace(".dat", "")
        self. directory = os.path.dirname(self.fileprefix)
        self._create_directory_and_load()
        if debug:
            print("cloudmesh.cc.db loading:", self.filename)

    @property
    def filename(self):
        if os_is_windows():
            return self.fileprefix + ".dat"
        else:
            return self.fileprefix + ".db"

    def _create_directory_and_load(self):
        directory = os.path.dirname(self.fileprefix)
        if not os.path.isdir(directory):
            Shell.mkdir(directory)
            self.data = shelve.open(self.fileprefix)
            self.save()
        else:
            self.load()

    def info(self):
        print("keys: ", self.__str__())
        print("n: ", len(self.data.keys()))
        print("filename: ", self.filename)
        print("fileprefix: ", self.fileprefix)


    def save(self):
        """
        save the data to the database

        Args:
            data ():

        Returns:

        """
        self.data.sync()

    def close(self):
        print("closing shelf")
        self.data.close()

    def load(self):
        """
        load the database and return as data

        Returns:

        """
        # self.data.load()
        self.data = shelve.open(self.filename)
        return self.data

    def remove(self):
        """
        remove the database
        Returns:

        """
        if os_is_windows():
            os.remove(f"{self.fileprefix}.bak")
            os.remove(f"{self.fileprefix}.dat")
            os.remove(f"{self.fileprefix}.dir")
        else:
            os.remove(f"{self.fileprefix}.db")

    def get(self, name):
        # special load for modification
        self.data = shelve.open(self.fileprefix, writeback=True)
        return self.data[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        # special load for modification
        self.data = shelve.open(self.fileprefix, writeback=True)
        self.data[key] = value
        self.save()

    def __str__(self):
        self.load()
        s = ""
        keylist = list(self.data.keys())
        for key in keylist:
            s += str(key) + ": " + str(self.data[key]) + "\n"
        return s

    def __delitem__(self, key):
        # special load for modification
        # IS THI RIGHT?????
        # ACCORDING TO DOCUMENTATION IT IS NOT
        self.data = shelve.open(self.fileprefix, writeback=True)
        del self.data[key]

    def clear(self):
        # self.data = {}
        self.load()
        keylist = list(self.data.keys())
        for key in keylist:
            del self.data[key]

        # self.data.clear()