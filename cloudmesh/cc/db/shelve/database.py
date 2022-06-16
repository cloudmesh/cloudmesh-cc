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
            self.filename = path_expand("~/.cloudmesh/queue/queues")
        self._create_directory_and_load()
        if debug:
            print("cloudmesh.cc.db loading:", self.filename)

    def _create_directory_and_load(self):
        directory = os.path.dirname(self.filename)
        if not os.path.isdir(directory):
            Shell.mkdir(directory)
            self.data["queues"] = {}
            self.save()
        else:
            self.load()

    def info(self):
        print("keys: ", self.data["queues"].keys())
        print("n: ", len(self.data['queues'].keys()))
        print("filename: ", self.filename)


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
        os.remove(f"{self.filename}.bak")
        os.remove(f"{self.filename}.dat")
        os.remove(f"{self.filename}.dir")

    def get(self, name):
        return self.data['queues'][name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        self.data['queues']['key'] = value
        self.save()

    def __str__(self):
        return self.data["queues"]

    def __delitem__(self, key):
        del self.data['queues'][key]

    def clear(self):
        self.data["queues"] = {}
        # with shelve.open(self.filename) as d:
        #     keylist = list(d.keys())
        #     for key in keylist:
        #         del d[key]

        # self.data.clear()