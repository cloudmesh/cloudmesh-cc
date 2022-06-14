from cloudmesh.cc.data import Data
from cloudmesh.common.Shell import Shell

# result = Shell.execute('pwd')
# print(result)
# result = Shell.execute('ls', ["-l", "-a"])
# print(result)
# result = Shell.execute('ls', "-l -a")
# print(result)

# d = Data('./directory')
# d.upload('text.txt')

r = Shell.run('ls')
print(r)