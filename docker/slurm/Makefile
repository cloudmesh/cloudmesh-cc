.PHONY:   manager node jupyter

image:  cloudmesh manager node jupyter
	docker image ls | fgrep slurm

cloudmesh:
	cd  ../cloudmesh; make image

manager:
	cd  manager; docker build -t slurm-manager:latest .

node:
	cd node;  docker build -t slurm-node:latest .

jupyter:
	cd jupyter; docker build -t slurm-jupyter:latest .

lab:
	open http://localhost:8888

start:
	docker-compose -f docker-compose-jupyter.yml up -d


stop:
	docker-compose -f docker-compose-jupyter.yml  stop

log:
	docker-compose -f docker-compose-jupyter.yml logs -

ps:
	docker-compose -f docker-compose-jupyter.yml ps

shell:
	docker run --rm -it slurm-manager:latest  /bin/bash

cleanall:
	-docker kill $$(docker ps -q)
	-docker rm -f $$(docker ps -a -q)
	-docker rmi -f $$(docker images -q)