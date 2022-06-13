from cloudmesh.common.Shell import Shell

result = Shell.execute('pwd')
print(result)
result = Shell.execute('ls', ["-l", "-a"])
print(result)
result = Shell.execute('ls', "-l -a")
print(result)
