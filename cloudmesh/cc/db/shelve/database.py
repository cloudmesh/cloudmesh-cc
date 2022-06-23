import os
import shelve

import yaml

from cloudmesh.common.Shell import Shell, Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_linux
import pathlib

#
# convert this to use shelve keep all methods signatures the same
#

class Database:

    #  Database()
    #  Database(filenae="a.db")   -> a.db only on linux and mac
    #  Database(filenae="a.dat")  -> a.dat only on windows

    #  Database(filenane="a")     -> a.db on linux and mac, .dat on windows

    # db["local"] -> local queue
    # db["queue"]["local"]
    # db.queues["local"]

    def __init__(self, name="queue", filename=None, debug=False):
        """
        filename is a prefix

        Args:
            filename ():
            debug ():
        """

        self.debug = debug

        if filename is None:
            filename = "~/.cloudmesh/queue/queues"
        filename = path_expand(filename)
        prefix = filename.replace(".dat","").replace(".db", "")

        self.fileprefix = prefix
        self.directory = os.path.dirname(self.fileprefix)

        if not os.path.isfile(self.filename):
            Shell.mkdir(self.directory)
            self.load()
            self.data["queue"] = {}
            self.data["config"] = {}
            self.save()
            self.close()


        self.load()

        self.data["config"] = {
            "filename" : filename,
            "name": name,
            "kind": "shelve"
        }

        if debug:
            self.info()

    @property
    def queues(self):
        return self.data["queue"]

    @property
    def queues(self):
        if "queue" not in self.data:
            self.data["queue"] ={}
        return self.data["queue"]

    @property
    def filename(self):
        if os_is_windows():
            return self.fileprefix + ".dat"
        elif os_is_mac() or os_is_linux():
            return self.fileprefix + ".db"
        else:
            raise ValueError("This os is not yet supported for shelve naming, please fix.")

    def info(self):
        return str(self)

    def load(self):
        """
        load the database and return as data

        Returns:

        """
        self.data = shelve.open(self.fileprefix, writeback=True)
        return self.data

    def save(self):
        """
        save the data to the database

        Args:
            data ():

        Returns:

        """
        self.data.sync()

    def close(self):
        self.data.close()

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
        return self.queues[name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        self.queues[key] = value
        self.save()

    def __str__(self):
        d = {
            "config": self.data["config"],
            "queue": self.data["queue"]
        }
        return str(yaml.dump(d, indent=2))


    def delete(self, key):
        # print(type(self.data["queues"]))
        if key in self.queues:
            del self.queues[key]
        self.save()

    def __delitem__(self, key):
        self.delete(key)

    def clear(self):
        self.data["queue"] = {}
        self.save()

    def __len__(self):
        return len(self.queues)
