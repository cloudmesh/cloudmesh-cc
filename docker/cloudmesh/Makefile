######################################################################
# DOCKER
######################################################################

include ../makefile.sys



image:
	docker build ${PROGRESS} -t cloudmesh/python:${VERSION} .

# --volume "${HOME}/.ssh:.ssh"
# --volume "${HOME}/.ssh:/root/.ssh"
# --user ${UID}:${GID}
# --volume "${PWD}/..:/data"

CM=$(shell find  ~ -type d -name 'cm' | head -n 1)
user_dir_name=$(shell basename $$HOME)

shell:
	@echo ${UID}
	@echo ${GID}
	@echo ${HOME}
	docker run \
	  --name cms \
	  -p 8000:8000 \
	  --rm  \
	  --volume "${CM}:${HOME}/cm" \
	  --volume "${HOME}/.cloudmesh:${HOME}/.cloudmesh" \
	  --volume "${HOME}/.local:${HOME}/.local" \
	  -it \
	  --user ${UID}:${GID} \
      --workdir="${HOME}/cm" \
      --volume "${HOME}/.ssh:${HOME}/.ssh:ro" \
      --volume="/etc/group:/etc/group:ro" \
      --volume="/etc/passwd:/etc/passwd:ro" \
      --volume="/etc/shadow:/etc/shadow:ro" \
	  cloudmesh/python:${VERSION} \
	  /bin/bash

login:
	docker exec -it cms /bin/bash

wshell:
	docker run \
	  --name cms \
	  --rm  -it \
	  --workdir="//home//${USERNAME}" \
	  --volume="//c//Users//${user_dir_name}://home//${USERNAME}" \
	  -p 80:80 \
	  -p 8000:8000 \
	  cloudmesh/python:latest \
	  "//bin//bash"

dshell:
	docker-compose run cms /bin/bash


cms:
	docker run --rm -it cloudmesh/python:${VERSION}

cleanall:
	-docker kill $$(docker ps -q)
	-docker rm -f $$(docker ps -a -q)
	-docker rmi -f $$(docker images -q)
	-docker volume rm $$(docker volume ls -q)
	-docker system prune -a -f --volumes

push:
	docker push cloudmesh/python:${VERSION}

run:
	docker run cloudmesh/python:${VERSION} /bin/sh -c "cd technologies; git pull; make"
