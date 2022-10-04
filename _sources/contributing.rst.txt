Contributing
============

GitHub
------

The code is maintained on GitHub

* `GitHub Issues <https://github.com/cloudmesh/cloudmesh-cc/issues>`_
* `GitHub Pull Requests <https://github.com/cloudmesh/cloudmesh-cc/pulls>`_

Management
----------

All contributions will be done under the apache license. The code will
be managed in open-source. Pull requests need to be made in the
repository. The main branch is the release branch. Contributions will
first be done in other branches, and once we agree that they need to be
integrated into the code, they will be merged into main. All new code
must have sufficient pytests. The pytests may need to be documented in
case special authentication is required.

We follow a `typical GitHub
workflow <https://docs.github.com/en/get-started/quickstart/github-flow>`__
of:

-  create a personal fork of this repo
-  create a branch
-  open a pull request
-  fix findings of various linters and checks
-  work through code review

For each pull request, the documentation is built and deployed to make
it easier to review the changes in the pull request.



Tests
-----

Before creating a pull request it is important that the tests in the
test directory pass.

The tests are organized as follows:

-  ``pytest tests/test_0??_*`` will run locally and only use ascii
   output

-  ``pytest tests/test_1??_*`` will run locally but also present graphs

.. todo:: in future we will likely change this and allow a test
   variable ``cms set test_with_graph=False/True`` and if it is not
   existent it is False. In case it is false the graohs will not be
   displayed. but the test will be run.
   This change will also allow tests with 1?? to be run on github
   workflows

-  ``pytest tests/test_5??_*`` will run on remote machines and require
   at this time rivanna from UVA

.. todo:: in future this test will be modified so we can specify the remote
   user and remote host ``cms set test_remote_user=TBD``
   ``cms set test_remote_host=TBD``. If they do not exist they will use the defualts from ssh config
   rivanna. verify if logic is ok.

-  ``pytest tests/test_6??_*`` will test the rest service

-  ``pytest tests/test_9??_*`` will cleanup the tests
