image:
	cd master; docker build -t slurm-master:latest .
	cd node;  docker build -t slurm-node:latest .
	cd jupyter; docker build -t slurm-jupyter:latest .
	docker image ls | fgrep slurm

start:
	docker-compose -f docker-compose-jupyter.yml up -d

stop:
	docker-compose -f docker-compose-jupyter.yml  stop

log:
	docker-compose -f docker-compose-jupyter.yml logs -

ps:
	docker-compose -f docker-compose-jupyter.yml ps

shell:
	docker run --rm -it slurm-master:latest  /bin/bash