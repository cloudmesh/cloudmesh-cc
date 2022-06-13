from cloudmesh.common.Shell import Shell

class Data:
    def __init__(self, directory):
        self.directory = directory

    def create(self, name=None):
        if name is not None:
            self.name = name
        Shell.execute(f'touch, {self.name}')

    def upload(self, name=None):
        if name is not None:
            self.name = name
        Shell.execute(f'mv {self.name} {self.directory}')


    def delete(self, name=None):
        if name is not None:
            self.name = name
        Shell.execute(f'rm {self.name}')

