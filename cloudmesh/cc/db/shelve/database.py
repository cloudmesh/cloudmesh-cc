import os
import shelve
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_linux
import pathlib

#
# convert this to use shelve keep all methods signatures the same
#

class Database:

    #  Databese()
    #  Database(filenae="a.db")   -> a.db only on linux and mac
    #  Database(filenae="a.dat")  -> a.dat only on windows

    #  Database(filenane="a")     -> a.db on linux and mac, .dat on windows

    def __init__(self, filename=None, debug=False):
        """
        filename is a prefix

        Args:
            filename ():
            debug ():
        """


        self.debug = debug

        if filename is None:
            filename = "~/.cloudmesh/queue/queues"
        self.fileprefix = path_expand(filename)

        self.fileprefix = self.fileprefix.replace(".db", "").replace(".dat", "")

        self.directory = os.path.dirname(self.fileprefix)

        if not os.path.isfile(self.filename):
            Shell.mkdir(self.directory)
            self.data = shelve.open(self.filename)
            self.data["filename"] = self.filename
            self.data["queues"] = {}
            self.save()
            self.close()
        self.load()

        if debug:
            self.info()

    @property
    def filename(self):
        if os_is_windows():
            return self.fileprefix + ".dat"
        elif os_is_mac() or os_is_linux():
            return self.fileprefix + ".db"
        else:
            raise ValueError("This os is not yet supported for shelve naming, pleaes fix.")

    def _create_(self):
        print ("CHECK", self.directory, self.fileprefix)

    def info(self):
        print("keys: ", self.__str__())
        print("n: ", len(self.data.keys()))
        print("queues:", self.data["queues"])
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
        self.data.close()

    def load(self):
        """
        load the database and return as data

        Returns:

        """
        # self.data.load()
        self.data = shelve.open(self.filename, writeback=True)
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
        return self.data["queues"][name]

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, key, value):
        self.data["queues"][key] = value
        self.save()

    def __str__(self):
        s = ""
        keylist = list(self.data.keys())
        for key in self.data:
            s += str(key) + ": " + str(self.data[key]) + "\n"
        return s

    def delete(self, key):
        print(type(self.data["queues"]))
        del self.data["queues"][key]
        self.save()

    def __delitem__(self, key):
        self.delete(key)

    def clear(self):
        keylist = list(self.data.keys())
        for key in keylist:
            del self.data[key]
        self.save()

    def __len__(self):
        return len(self.data["queues"])
