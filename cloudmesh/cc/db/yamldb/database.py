import os

from yamldb import YamlDB

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand


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
            # self.data = {}
            # self.save()

        self.data = YamlDB(filename=self.filename)
        self.data["config"] = {}
        self.data["config.filename"] = self.filename
        self.data["config.name"] = self.name
        self.data["config.kind"] = "yamldb"

        self.data.save(self.filename)
        if debug:
            print("cloudmesh.cc.db loading:", self.filename)

    def save(self, filename=None):
        """
        save the data to the database
        """
        if filename is None:
            self.data.save(filename=self.filename)
        else:
            self.data.save(filename=filename)

    def load(self, filename=None):
        """
        load the database and return as data

        Returns:

        """
        if filename is None:
            self.data.load(filename=self.filename)
        else:
            self.data.load(filename=filename)

    def remove(self):
        """
        remove the database
        Returns:

        """
        os.remove(self.filename)

    def get(self, name):
        return self.data[name]

    def get_queue(self, name):
        return self.data['queue'][name]

    def get_job(self, queue=None, name=None):
        queue = self.get_queue(queue)
        return queue[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        return str(self.data)

    def clear(self):
        self.data.clear()

    @property
    def queues(self):
        if "queue" not in self.data:
            self.data["queue"] = {}
        return self.data["queue"]

    def info(self):
        return str(self.data)
