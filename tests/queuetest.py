from cloudmesh.cc.cmqueue import CMQueue


q = CMQueue()

names = []
commands = []

for i in range(0, 10):
    job = "Job", i
    names.append(job)
    commands.append(i)

for i in range(0, len(names)):
    q.add(names[i], commands[i])
    print('Added names and commands')
print()


for i in range(0, len(names)):
    q.remove(names[i])
    q.status(names[i])
    q.list()
