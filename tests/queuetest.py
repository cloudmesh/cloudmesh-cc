from cloudmesh.cc.command.queue import Queue
from cloudmesh.cc.command.queue import Job

q = Queue()
queuenames = ['localuser', 'rivanna1', 'rivanna2', 'rivanna3']
for name in queuenames:
    q.create(queuename=name)

print('Adding to queue . . .')
print()
for name in queuenames:
    for x in range(0, 9):
        jobname = f"job-{x}"
        command = f"echo Hello world {x}"
        q.add(jobname=jobname, queuename=name, command=command)
print("Finished adding to the queue . . . ")
print()
'''
q.list(queuename="localuser")

print('Removing from queue . . . ')
print()


q.remove(queuename='rivanna1')
q.list(queuename='rivanna1')


print("Finished removing from queue . . . ")

'''
q.run('rivanna1')