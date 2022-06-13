from cloudmesh.common.Shell import Shell

class Data:
    def __init__(self, directory):
        self.directory = directory

    def upload(self, name=None, directory=None):
        if name is not None:
            self.name = name
        if directory is not None:
            self.directory=directory
        Shell.execute(f'cd, {self.directory}')
        Shell.execute(f'touch, {self.name}')
        Shell.execute(f'mv {self.name} {self.directory}')


    def delete(self, name=None, directory=None):
        if name is not None:
            self.name = name
        if directory is not None:
            self.directory = directory
        Shell.execute(f'cd, {self.directory}')
        Shell.execute(f'rm {self.name}')

