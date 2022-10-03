package=cc
UNAME=$(shell uname)
VERSION=`head -1 VERSION`

.PHONY: conda docs

ifeq ($(OS),Windows_NT)
detected_OS := Windows
else
detected_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
endif

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

define banner
	@echo
	@echo "############################################################"
	@echo "# $(1) "
	@echo "############################################################"
endef

source:
	$(call banner, "Install cloudmesh-common")
	pip install -e . -U

flake8:
	flake8 cloudmesh

#cd ..; flake8 --max-line-length 124 --ignore=E722 cloudmesh-$(package)/cloudmesh
#cd ..; flake8 --max-line-length 124 --ignore=E722 cloudmesh-$(package)/tests

pylint:
	cd ..; pylint --rcfile=cloudmesh-$(package)/.pylintrc  cloudmesh-$(package)/cloudmesh
	cd ..; pylint --rcfile=cloudmesh-$(package)/.pylintrc  --disable=F0010 cloudmesh-$(package)/tests

requirements:
	echo "# cloudmesh-common requirements"> tmp.txt
	#echo "cloudmesh-common" > tmp.txt
	#echo "cloudmesh-cmd5" >> tmp.txt
	# pip-compile setup.py
	cat requirements.txt >> tmp.txt
	mv tmp.txt requirements.txt
	-git commit -m "update requirements" requirements.txt
	-git push

test:
	pytest -v --html=.report.html
	open .report.html

dtest:
	pytest -v --capture=no

clean:
	$(call banner, "CLEAN")
	rm -rf *.zip
	rm -rf *.egg-info
	rm -rf *.eggs
	rm -rf docs/build
	rm -rf api/build
	rm -rf build
	rm -rf dist
	find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
	rm -rf .tox
	rm -f *.whl
	rm -rf docs/source/generated
	rm -rf docs/source/cloudmesh.cc.*.rst
	rm -rf docs/source/cloudmesh.cc.rst
	rm -rf docs/source/cloudmesh.rst

clear:
	rm -rf ~/experiment
	ssh rivanna "rm -rf experiment" 
	-rm -f *.error
	-rm -f *.log
	-rm -f job-local-*
	-rm -f job-rivanna.hpc.virginia.edu*
	-rm -f run.sh slurm.sh *-slurm.sh run-killme.sh start.sh test-*.sh end.sh
	-rm -f *.dot *.svg
	-rm -rf dest
	-rm -f hello-world.py

www:
	cd cloudmesh/cc/service/markdown ; curl https://raw.githubusercontent.com/cloudmesh/cloudmesh-cc/main/README.md -o README.md

######################################################################
# PYPI
######################################################################


twine:
	pip install -U twine

dist:
	python setup.py sdist bdist_wheel
	twine check dist/*

patch: clean twine
	$(call banner, "patch")
	bump2version --allow-dirty patch
	python setup.py sdist bdist_wheel
	git push origin main --tags
	twine check dist/*
	twine upload --repository testpypi  dist/*
	# $(call banner, "install")
	# pip search "cloudmesh" | fgrep cloudmesh-$(package)
	# sleep 10
	# pip install --index-url https://test.pypi.org/simple/ cloudmesh-$(package) -U

minor: clean
	$(call banner, "minor")
	bump2version minor --allow-dirty
	@cat VERSION
	@echo

release: clean
	$(call banner, "release")
	git tag "v$(VERSION)"
	git push origin main --tags
	python setup.py sdist bdist_wheel
	twine check dist/*
	twine upload --repository pypi dist/*
	$(call banner, "install")
	@cat VERSION
	@echo
	# sleep 10
	# pip install -U cloudmesh-common


dev:
	bump2version --new-version "$(VERSION)-dev0" part --allow-dirty
	bump2version patch --allow-dirty
	@cat VERSION
	@echo

reset:
	bump2version --new-version "4.0.0-dev0" part --allow-dirty

upload:
	twine check dist/*
	twine upload dist/*

pip:
	pip install --index-url https://test.pypi.org/simple/ cloudmesh-$(package) -U

#	    --extra-index-url https://test.pypi.org/simple

log:
	$(call banner, log)
	gitchangelog | fgrep -v ":dev:" | fgrep -v ":new:" > ChangeLog
	git commit -m "chg: dev: Update ChangeLog" ChangeLog
	git push

# bump:
#	git checkout main
#	git pull
#	tox
#	python setup.py sdist bdist_wheel upload
#	bumpversion --no-tag patch
#	git push origin main --tags


######################################################################
# SPHINX
######################################################################

man:
	cd docs; make man

requirements-dev:
	pip install -r requirements-dev.txt

doc: requirements-dev man
	cd docs; sphinx-apidoc ../cloudmesh -o source
	cd docs; make html


latex:
	cd api; make latexpdf

#docs:
#	rsync --size-only -av api/build/html/* docs


view:
ifeq ($(detected_OS),Windows)
	cmd //C "start firefox file://$(mkfile_dir)docs/build/html/index.html"
endif
ifeq ($(detected_OS),Darwin)        # Mac OS X
	$(shell open docs/build/html/index.html)
endif
ifeq ($(detected_OS),Linux)
	$(shell firefox docs/build/html/index.html)
endif

