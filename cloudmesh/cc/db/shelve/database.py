import os
import shelve
# from cloudmesh.common.Shell import Shell
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

        print("D", self.directory)
        print("F", self.filename)

        if not os.path.isfile(self.filename):
            pathlib.Path.mkdir(self.directory, exist_ok=True)
            self.data = shelve.open(self.filename)
            self.data["filename"] = self.filename
            self.save()
            self.close()
            print("OOOOO")

        self.load()

        if debug:
            print("cloudmesh.cc.db loading:", self.filename)

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
        s = ""
        keylist = list(self.data.keys())
        for key in self.data:
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