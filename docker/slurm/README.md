# slurm-cluster

Adapted from:

* <https://github.com/rancavil/slurm-cluster>
* <https://medium.com/analytics-vidhya/slurm-cluster-with-docker-9f242deee601>


Docker local slurm cluster

To run slurm cluster environment you must execute:

     $ docker-compose -f docker-compose-jupyter.yml up -d

To stop it, you must:

     $ docker-compose -f docker-compose-jupyter.yml stop

To check logs:

     $ docker-compose -f docker-compose-jupyter.yml logs -f

     (stop logs with CTRL-c")

To check running containers:

     $ docker-compose -f docker-compose-jupyter.yml ps
