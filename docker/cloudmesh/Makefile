######################################################################
# DOCKER
######################################################################

include ../makefile.sys

image:
	docker build ${PROGRESS} -t cloudmesh/python:${VERSION} .

# --volume "${HOME}/.ssh:.ssh"
# --volume "${HOME}/.ssh:/root/.ssh"
# --user ${USER_ID}:${GROUP_ID}
# --volume "${PWD}/..:/data"

shell:
	@echo ${USER_ID}
	@echo ${GROUP_ID}
	docker run --rm  -it \
	  --volume "${HOME}:${HOME}" \
	  -it cloudmesh/python:${VERSION} \
	  --user ${USER_ID}:${GROUP_ID} \
      --workdir="${HOME}" \
      --volume="/etc/group:/etc/group:ro" \
      --volume="/etc/passwd:/etc/passwd:ro" \
      --volume="/etc/shadow:/etc/shadow:ro" \
	  /bin/bash


cms:
	docker run --rm -it cloudmesh/python:${VERSION}

cleanall:
	-docker kill $$(docker ps -q)
	-docker rm -f $$(docker ps -a -q)
	-docker rmi -f $$(docker images -q)

push:
	docker push cloudmesh/python:${VERSION}

run:
	docker run cloudmesh/python:${VERSION} /bin/sh -c "cd technologies; git pull; make"
