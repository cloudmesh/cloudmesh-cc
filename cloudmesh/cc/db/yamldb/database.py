import os
from yamldb import YamlDB
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
import pathlib


class Database:

    def __init__(self, name="queue", filename=None, debug=False):
        self.debug = debug
        self.name = name

        if filename is None:
            filename = "~/.cloudmesh/queue/queues.yaml"
        self.filename = path_expand(filename)

        self.fileprefix = path_expand(filename)
        # self.name = name

        directory = os.path.dirname(self.fileprefix)
        if not os.path.isdir(directory):
            Shell.mkdir(directory)
            self.data = {}
            self.save()


        self.db = YamlDB(filename=self.filename)
        self.db["config"] = {}
        self.db["config.filename"] = self.filename
        self.db["config.name"] = self.name

        self.db.save(self.filename)
        if debug:
            print("cloudmesh.cc.db loading:", self.filename)


    def save(self):
        """
        save the data to the database

        Args:
            data ():

        Returns:

        """
        self.db.save(filename=self.filename)

    def load(self):
        """
        load the database and return as data

        Returns:

        """
        self.db.load(filename=self.filename)

    def remove(self):
        """
        remove the database
        Returns:

        """
        os.remove(self.filename)

    def get(self, name):
        return self.db[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        self.db[key] = value

    def __str__(self):
        return str(self.db)

    def clear(self):
        self.db.clear()
