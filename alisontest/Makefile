######################################################################
# DOCKER
######################################################################

include makefile.sys



image:
	docker build ${PROGRESS} -t cloudmesh/python:${VERSION} .

# --volume "${HOME}/.ssh:.ssh"
# --volume "${HOME}/.ssh:/root/.ssh"
# --user ${UID}:${GID}
# --volume "${PWD}/..:/data"

shell:
	@echo ${UID}
	@echo ${GID}
	@echo ${HOME}
	docker run --rm  \
	  --volume "${HOME}:${HOME}" \
	  -it \
	  --user ${UID}:${GID} \
      --workdir="${HOME}" \
      --volume="/etc/group:/etc/group:ro" \
      --volume="/etc/passwd:/etc/passwd:ro" \
      --volume="/etc/shadow:/etc/shadow:ro" \
	  cloudmesh/python:${VERSION} \
	  /bin/bash


wshell:
	docker run --rm  -it \
	  --workdir="//home//${USERNAME}//cm//cloudmesh-cc" \
	  --volume="//c//Users//${USERNAME}://home//${USERNAME}" \
	  cloudmesh/python:latest \
	  "//bin//bash"

a:
	docker run \
	  --name cms \
	  --workdir="//home//${USERNAME}//cm//cloudmesh-cc" \
	  --volume="//c//Users//${USERNAME}://home//${USERNAME}" \
	  -p 8000:8000 cloudmesh/python:latest

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
