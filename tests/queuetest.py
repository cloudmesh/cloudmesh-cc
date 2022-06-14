from cloudmesh.cc.command.queue import Queue
from cloudmesh.cc.command.queue import Job


q = Queue()
for name in ['localuser', 'rivanna1', 'rivanna2', 'rivanna3']:
    q.create(queuename=name)



print('Adding to queue . . .')
for i in range(0, 9):
    name = f"job-{i}"
    job = Job(jobname=name, command=f"sleep 0.{i}")
    q.add(jobname=job, queuename='localuser')
print()
print("Finished adding to the queue . . . ")

q.list(queuename="localuser")


'''
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


'''




