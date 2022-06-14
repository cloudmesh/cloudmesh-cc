from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import writefile
import os

class Data:
    global directory

    def __init__(self, directory):
        self.directory = directory


    def upload(self, name=None):
        if name is not None:
            self.name = name
        self.directory=
        writefile(f'{self.directory}/{self.name}')
        file.close()


    # def upload(self, name=None, directory=None):
    #     if name is not None:
    #         self.name = name
    #     if directory is not None:
    #
# <<<<<<< HEAD
#             self.directory=directory
#         Shell.mkdir(self.directory)
#         Shell.run(f'cd {self.directory}')
#         Shell.run(f'touch {self.name}')
#         Shell.run(f'mv {self.name} {self.directory}')
# =======
#             self.directory = directory
#         Shell.execute(f'mkdir -p {self.directory}')
#         Shell.execute(f'cd {self.directory}')
#         Shell.execute(f'touch {self.name}')
#         Shell.execute(f'mv {self.name} {self.directory}')
# >>>>>>> 66d75a0b129ddae19e4f1a7acd0fd5cea0324dae
#
#     def delete(self, name=None, directory=None):
#         if name is not None:
#             self.name = name
#         if directory is not None:
#             self.directory = directory
# <<<<<<< HEAD
#         Shell.run(f'cd {self.directory} && rm {self.name}')
#
# =======
#         Shell.execute(f'cd {self.directory}')
#         Shell.execute(f'rm {self.name}')
# >>>>>>> 66d75a0b129ddae19e4f1a7acd0fd5cea0324dae
