import os
import shelve

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
import pathlib

#
# convert this to use shelve keep all methods signatures the same
#

class Database:

    def __init__(self, filename=None, debug=False):
        self.debug = debug
        if filename:
            self.filename = filename
        else:
            self.filename = path_expand("~/.cloudmesh/queue/queues.yaml")

        self.d = shelve.open(filename=self.filename)
        self.d.close()
        if debug:
            print("cloudmesh.cc.db loading:", self.filename)

    def _create_directory(self):
        directory = os.path.dirname(self.filename)
        if not os.path.isdir(directory):
            Shell.mkdir(directory)
            self.data = {}
            self.save()

    def save(self):
        """
        save the data to the database

        Args:
            data ():

        Returns:

        """
        self.d.close()

    def load(self):
        """
        load the database and return as data

        Returns:

        """
        # self.db.load()
        with shelve.open(self.filename) as d:
            return d

    def remove(self):
        """
        remove the database
        Returns:

        """
        os.remove(f"{self.filename}.bak")
        os.remove(f"{self.filename}.dat")
        os.remove(f"{self.filename}.dir")

    def get(self, name):
        with shelve.open(self.filename) as d:
            return d[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        with shelve.open(self.filename) as d:
            d[key] = value

    def __str__(self):
        s = "Shelve: " + self.filename
        with shelve.open(self.filename) as d:
            keylist = list(d.keys())
            for key in keylist:
                s += "\n" + key + ": " + str(d[key])
        return s

    def clear(self):
        with shelve.open(self.filename) as d:
            keylist = list(d.keys())
            for key in keylist:
                del d[key]

        # self.db.clear()