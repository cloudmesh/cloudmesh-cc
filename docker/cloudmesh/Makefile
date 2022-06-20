######################################################################
# DOCKER
######################################################################

VERSION=latest

image:
	docker build -t cloudmesh/python:${VERSION} .

shell:
	docker run --rm -it cloudmesh/python:${VERSION}  /bin/bash

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
