###############################################################
# pytest -v --capture=no tests/test_012_service_localhost.py
# pytest -v  tests/test_012_service_localhost.py
# pytest -v --capture=no  tests/test_012_service_localhost.py::TestService::<METHODNAME>
###############################################################
import time
import yaml
import requests
import pytest
from fastapi.testclient import TestClient
from cloudmesh.cc.service.service import app
from cloudmesh.common.util import HEADING
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Shell import Console
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.cc.service.service import get_available_workflows
from httpx import AsyncClient
import os
from pathlib import Path

client = TestClient(app)

@pytest.mark.incremental
class TestService:

    def test_start_over(self):
        HEADING()
        Benchmark.Start()
        list_of_workflows_to_delete = []
        example_workflow_dir = Shell.map_filename(
            '~/.cloudmesh/workflow/workflow-example/').path
        testing_workflow_dir = Shell.map_filename(
            '~/.cloudmesh/workflow/imtesting').path
        list_of_workflows_to_delete.append(example_workflow_dir)
        list_of_workflows_to_delete.append(testing_workflow_dir)
        for workflow_dir in list_of_workflows_to_delete:
            try:
                Shell.run(f'rm -rf {workflow_dir}')
            except Exception as e:
                print(e)
            assert not os.path.exists(workflow_dir)
        Benchmark.Stop()

    @pytest.mark.anyio
    async def test_home(self):
        HEADING()
        Benchmark.Start()
        async with AsyncClient(app=app, base_url="http://127.0.0.1") as ac:
            response = await ac.get("/")
        assert response.status_code == 200
        Benchmark.Stop()

    def test_list_workflows(self):
        HEADING()

        Benchmark.Start()
        response = client.get("/workflows")
        print(response.json())
        # result = Shell.run("ls ~/.cloudmesh/workflow").splitlines()
        result = get_available_workflows()
        print(result)
        assert len(response.json()['workflows']) == len(result)
        assert response.status_code == 200
        # assert response.json() == {"workflows":list}
        Benchmark.Stop()

    def test_upload(self):
        HEADING()

        Benchmark.Start()

        # we are catching the scenario where the user does not have cm dir in ~
        test_file = Path(f'{__file__}').as_posix()
        test_dir = Path(os.path.dirname(test_file)).as_posix()
        example_dir = os.path.join(test_dir, 'workflow-example')
        example_dir = example_dir.replace("\\", "/")
        expanded_user = os.path.expanduser('~')
        expanded_user = expanded_user.replace('\\', '/')
        if expanded_user in example_dir:
            example_dir = example_dir.replace(expanded_user, '~')

        response = client.post(f"/workflow?directory={example_dir}")
        Benchmark.Stop()
        print(response.json())
        assert response.status_code == 200
        assert 'Successfully uploaded' in response.json()['message']

    def test_upload_two(self):
        HEADING()

        Benchmark.Start()

        # we are trying out the name parameter in upload
        test_file = Path(f'{__file__}').as_posix()
        test_dir = Path(os.path.dirname(test_file)).as_posix()
        example_dir = os.path.join(test_dir, 'workflow-example')
        example_dir = example_dir.replace("\\", "/")
        expanded_user = os.path.expanduser('~')
        expanded_user = expanded_user.replace('\\', '/')
        if expanded_user in example_dir:
            example_dir = example_dir.replace(expanded_user, '~')

        response = client.post(
            f"/workflow?directory={example_dir}&name=imtesting")
        Benchmark.Stop()
        assert response.status_code == 200
        assert 'Successfully uploaded' in response.json()['message']

    def test_retrieve_workflow(self):
        HEADING()

        Benchmark.Start()

        responsejob = client.get("/workflow/workflow-example/job/start")
        response = client.get("/workflow/workflow-example")
        # print(responsejob.json())
        # from pprint import pprint
        # pprint(response.json())
        Benchmark.Stop()
        assert 'echo hello' in responsejob.json()['start']['exec']
        assert 'compute' in response.json()['workflow-example']['graph']['nodes']
        assert 'fetch-data' in response.json()['workflow-example']['graph']['nodes']
        assert response.status_code == 200
        assert responsejob.ok

    def test_run_workflow(self):
        HEADING()

        Benchmark.Start()
        example_workflow_dir = Shell.map_filename(
            '~/.cloudmesh/workflow/workflow-example'
        ).path
        os.chdir(example_workflow_dir)
        response = client.get("/workflow/run/workflow-example")
        # print(response.json())
        Benchmark.Stop()
        assert response.status_code == 200

    def test_see_if_run_is_done(self):
        HEADING()

        Benchmark.Start()
        example_workflow_runtime_yaml = Shell.map_filename(
            fr'~/.cloudmesh/workflow/workflow-example/runtime/workflow-example.yaml'
        ).path
        interval = 32
        time.sleep(interval)
        runtime_yaml = yaml.safe_load(
            Path(example_workflow_runtime_yaml).read_text())
        try:
            if runtime_yaml['workflow']['nodes']['end']['progress'] == '100':
                assert True
        except Exception as e:
            print('failed')
            print(e.output)

            Console.error("Something is wrong...")
            assert False
        Benchmark.Stop()

    def test_add_job(self):

        HEADING()

        Benchmark.Start()
        #job = '{"name": "string","user": "string","host": "string","label": "string","kind": "string","status": "string","progress": 0,"script": "string","pid": 0,"parent": "string"}'
        job = "theAddJobWorked"
        user = "string"
        host = "string"
        label = "string"
        kind = "string"
        status = "string"
        progress = 2
        script = "string"

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        response = client.post(f"/workflow/workflow-example/job/{job}?user={user}&host={host}&label={label}&kind={kind}&status={status}&progress={progress}&script={script}")
        Benchmark.Stop()
        assert job in response.json()['jobs']
        assert response.ok

    def test_delete_workflow(self):
        HEADING()

        Benchmark.Start()
        # delete will not work if you stand in the workflow-example dir
        os.chdir('..')
        # now that we backed out and move up one directory, delete works
        response = client.delete("/workflow/workflow-example")
        Benchmark.Stop()
        workflow_example_dir = Shell.map_filename(
            '~/.cloudmesh/workflow/workflow-example'
        ).path
        assert 'was deleted' in response.json()['message']
        assert not os.path.isdir(workflow_example_dir)
        assert response.status_code == 200
        response = client.delete("/workflow/imtesting")
        assert 'was deleted' in response.json()['message']


