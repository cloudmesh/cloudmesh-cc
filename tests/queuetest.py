from cloudmesh.cc.cmqueue import CMQueue
from cloudmesh.cc.cmqueue import Job


q = CMQueue()
q.create('localuser')
q.create('rivanna1')
q.create('rivanna2')
q.create('rivanna3')




print('Adding to queue . . .')
for i in range(0, 100):
    j = Job(name=i, command=i)
    q.add(job=j, queuename='localuser')
    print(q.get('localuser'))
    q.add(job=j, queuename='rivanna1')
    q.add(job=j, queuename='rivanna2')
    q.add(job=j, queuename='rivanna3')


print('Removing from queue . . . ')
for i in range(0, 100):
    j = Job(name=i, command=i)
    q.remove(job=j, queuename='localuser')
    print(q.get('localuser'))
    q.remove(job=j, queuename='rivanna1')
    q.remove(job=j, queuename='rivanna2')
    q.remove(job=j, queuename='rivanna3')







