######################################################################
# DOCKER
######################################################################

include ../makefile.sys

CWD=$(shell pwd)
CWD2=${HOME}

image:
	docker build ${PROGRESS} -t cloudmesh/python:${VERSION} .

shell:
	docker run --rm -it cloudmesh/python:${VERSION}  /bin/bash

a:
	echo ${CWD2}
	docker run --rm -v ${CWD2}:/data -it cloudmesh/python:${VERSION}  /bin/bash

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
