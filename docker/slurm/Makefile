.PHONY:   manager node jupyter cloudmesh lab start stop

include ../makefile.sys

image:  cloudmesh manager node jupyter
	docker image ls | fgrep slurm

cloudmesh:
	@echo
	@echo "#################################################"
	@echo "# cloudmesh"
	@echo "#################################################"
	@echo
	cd  ../cloudmesh; make image

manager:
	@echo
	@echo "#################################################"
	@echo "# manager"
	@echo "#################################################"
	@echo
	cd  manager; docker build ${PROGRESS} -t slurm-manager:latest .

node:
	@echo
	@echo "#################################################"
	@echo "# node"
	@echo "#################################################"
	@echo
	cd node;  docker build ${PROGRESS} -t slurm-node:latest .

jupyter:
	@echo
	@echo "#################################################"
	@echo "# jupyter"
	@echo "#################################################"
	@echo
	cd jupyter; docker build ${PROGRESS} -t slurm-jupyter:latest .

lab:
	@echo
	@echo "#################################################"
	@echo "# lab"
	@echo "#################################################"
	@echo
	open http://localhost:8888

start:
	@echo
	@echo "#################################################"
	@echo "# start"
	@echo "#################################################"
	@echo
	docker-compose -f docker-compose-jupyter.yml up -d


stop:
	@echo
	@echo "#################################################"
	@echo "# stop"
	@echo "#################################################"
	@echo
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
	-docker volume rm $$(docker volume ls -q)