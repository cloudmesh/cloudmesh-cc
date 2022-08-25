from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.StopWatch import progress
from cloudmesh.common.Shell import Shell

import time

filename = Shell.map_filename('./c.log').path

for i in [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
    progress(progress=i, filename=filename)
    time.sleep(0.8)