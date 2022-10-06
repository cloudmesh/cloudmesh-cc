"""Unused cloudmesh cc class for YamlDB database."""
import os

from yamldb import YamlDB

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand


class Database:
    """Unused cloudmesh cc class for YamlDB database."""
    def __init__(self, name="queue", filename=None, debug=False):
        """
        Initializes a yaml database in which each element is a string

        :param name: name of the database. If set it is stored in
                     ~/.cloudmesh/name/name.yaml if not overwritten by filename
        :type name: string
        :param filename: the filename. The default is "~/.cloudmesh/queue/queues.yaml"
        :type filename: string
        :param debug: prints debug messages if true
        :type debug: bool
        """
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
        Save the data to the database to the specified filename.
        If the filename is ommited it will save it to the filename sat at init.

        :param filename: the filename
        :type filename: string
        :return: None
        """
        if filename is None:
            self.data.save(filename=self.filename)
        else:
            self.data.save(filename=filename)

    def load(self, filename=None):
        """
        Load the database and return as data

        :param filename: the filename
        :type filename: string
        :return: None
        """
        if filename is None:
            self.data.load(filename=self.filename)
        else:
            self.data.load(filename=filename)

    def remove(self):
        """
        Remove the database
        """
        os.remove(self.filename)

    def get(self, name):
        """
        Gets the element with the specified name

        :param name: the name of the element in the database
        :type name: string
        :return: the content of name
        :rtype: string
        """
        return self.data[name]

    def get_queue(self, name):
        """
        Returns the Queue with the given name

        :param name: the name of the queue
        :type name: string
        :return: thr queu with the given name
        :rtype: dict
        """
        return self.data['queue'][name]

    def get_job(self, queue=None, name=None):
        """
        Returns a job from the queue by its name and the queue name.

        :param queue: the queue name
        :type queue: string
        :param name: the name of teh jobe
        :type name: the queue name
        :return: the job
        :rtype: dict
        """
        queue = self.get_queue(queue)
        return queue[name]

    def __getitem__(self, name):
        """
        returns the object with the given name

        :param name: name of the object
        :type name: string
        :return: content of the object with the name
        :rtype: dict
        """
        return self.get(name)

    def __setitem__(self, key, value):
        """
        Sets the item with the key to value

        :param key: the key
        :type key: string
        :param value: value
        :type value: object
        :return: None
        """
        self.data[key] = value

    def __str__(self):
        """
        String representation of the database

        :return: content
        :rtype: string
        """
        return str(self.data)

    def clear(self):
        """
        Removes all data

        :return: None
        """
        self.data.clear()

    @property
    def queues(self):
        """
        Lists all queues

        :return: names of teh queues
        :rtype: list
        """
        if "queue" not in self.data:
            self.data["queue"] = {}
        return self.data["queue"]

    def info(self):
        """
        prints all data of the DB

        :return: content
        :rtype: str
        """
        return str(self.data)
