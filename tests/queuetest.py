from cloudmesh.cc.queue import Queue
from cloudmesh.cc.queue import Job


q = Queue()
for name in ['localuser', 'rivanna1', 'rivanna2', 'rivanna3']:
    q.create(name)



print('Adding to queue . . .')
for i in range(0, 9):
    name = f"job-{i}"
    job = Job(name=name, command="sleep 0.{i}")
    q.add(job=job, queuename='localuser')
    for r in range(0,3):
        job = Job(name=f"rivanna-{name}", command="sleep 0.{i}")

q.list("")

for i in range(0, 9):
    name = f"job-{i}"
    print(q.get(job=name, queue='localuser'))


print('Removing from queue . . . ')
for i in range(0, 100):
    name = f"job-{i}"
    j = Job(name=i, command=i)
    q.remove(job=name)
    q.remove(job=j, queuename='rivanna1')
    q.remove(job=j, queuename='rivanna2')
    q.remove(job=j, queuename='rivanna3')







