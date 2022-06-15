import textwrap
from cloudmesh.common.Shell import Shell
from cloudmesh.cc.queue import Queue
import sys
"""
    This is the test file for the queue framework. Essentially, what we want
    is to create a queue, add some jobs to it, remove some jobs from it, list
    the contents of the queue, and then eventually run the rest of the commands
    that are in the queue.

    Section 1:
    Task 1: Create 1 queue object and add 5 jobs to it
    Task 2: From the queue object, remove 2 jobs
    Task 3: List the contents of the queue
    Task 4: Run the queue

    Section 2:
    Task 1: Create 3 queue objects and add 5 jobs to each of the queues (could just be print jobs)
    Task 2: Creates a queues object and add the 3 queues to the object
    Task 3: List the contents of the queues object
    Task4: Run the queues object in a FIFO order
"""

''' q = Queue()
for x in range(0, 9):
    q.add(f"job{x}", f"echo hello world {x}")

#q.list()

q.run(scheduler='fifo')
'''








# script for section 1:
"""
cms cc add --queue=a --jobname="Job2" --command="ls"
cms cc add --queue=a --jobname="Job3" --command="cd Desktop"
cms cc add --queue=a --jobname="Job4" --command="ls"
cms cc add --queue=a --jobname="Job5" --command="cd .."
cms cc list --queue=a
cms cc remove --queue=a --jobname="Job5"
cms cc remove --queue=a --jobname="Job4"
cms cc list --queue=a
cms cc run --queue=a
"""
script = textwrap.dedent(
"""
cms cc add --queue=a --job=\"Job1\" --command=\"cd\"
"""
).strip().splitlines()

print(script)

for command in script:
    print(command)
    c = Shell.run(command)
    print(c)


# script for section 2:
'''
s_2 = textwrap.dedent(
"""
cms cc queue --queue=a
cms cc queue add --queue=a --jobname="Job1" --command="echo queue a"
cms cc queue add --queue=a --jobname="Job2" --command="cd ~"
cms cc queue add --queue=a --jobname="Job3" --command="ls"
cms cc queue add --queue=a --jobname="Job4" --command="cd Desktop"
cms cc queue add --queue=a --jobname="Job5" --command="echo queue a done"
cms cc queue --queue=b
cms cc queue add --queue=b --jobname="Job1" --command="echo queue b"
cms cc queue add --queue=b --jobname="Job2" --command="cd ~"
cms cc queue add --queue=b --jobname="Job3" --command="ls"
cms cc queue add --queue=b --jobname="Job4" --command="cd Desktop"
cms cc queue add --queue=b --jobname="Job5" --command="echo queue b done"
cms cc queue --queue=c
cms cc queue add --queue=c --jobname="Job1" --command="echo queue c"
cms cc queue add --queue=c --jobname="Job2" --command="cd ~"
cms cc queue add --queue=c --jobname="Job3" --command="ls"
cms cc queue add --queue=c --jobname="Job4" --command="cd Desktop"
cms cc queue add --queue=c --jobname="Job5" --command="echo queue c done"
cms cc queues --queues=abc
cms cc queues add --queues=abc --queue=a
cms cc queues add --queues=abc --queue=b
cms cc queues add --queues=abc --queue=c
cms cc queues list --queues=abc
cms cc queues run --queues=abc
""").strip().splitlines()

print(s_2)
'''