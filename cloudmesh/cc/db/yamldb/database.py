import os
from yamldb import YamlDB

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
import pathlib


class Database:

    def __init__(self, filename=None, debug=False):
        self.debug = debug
        if filename:
            self.filename = filename
        else:
            self.filename = path_expand("~/.cloudmesh/queue/queues.yaml")
        self._create_directory()
        self.db = YamlDB(filename=self.filename)
        self.db["config.filename"] = self.filename
        self.db.save(self.filename)
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
        self.db.save()

    def load(self):
        """
        load the database and return as data

        Returns:

        """
        self.db.load()

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
