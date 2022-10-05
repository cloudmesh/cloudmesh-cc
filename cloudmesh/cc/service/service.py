"""Cloudmesh cc FastAPI service for REST and web interfaces."""
import glob
import io
import json
import os
import posixpath
import threading
from collections import Counter
from pathlib import Path
from pprint import pprint

import markdown
import networkx as nx
import pandas as pd
import pkg_resources
import time
import yaml
from fastapi import FastAPI, Query
from fastapi import Request, Form
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from cloudmesh.cc.__version__ import version as cm_version
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common.variables import Variables

"""
all the URLs.
@app.get("/", tags=['workflow'])
@app.get("/workflows", tags=['workflow'])
    ?json
    ?yaml
    ?html
    ?dict
    
@app.post("/workflow/upload", tags=['workflow'])
@app.delete("/workflow/{name}", tags=['workflow'])
@app.get("/workflow/{name}", tags=['workflow'])
@app.get("/workflow/run/{name}", tags=['workflow'])
@app.post("/workflow/{name}", tags=['workflow'])
"""

variables = Variables()

# debug = variables['debug']
# debug = False
debug = True

#
# set if portal routes should be displayed in the documentation
#
# include_portal_tag_in_schema = debug
include_portal_tag_in_schema = False


def get_available_workflows():
    """
    returns workflow dirs found in .cloudmesh directory

    :return: names of workflows found
    :rtype: list
    """
    folders = []
    directory = path_expand(f"~/.cloudmesh/workflow/")
    result = glob.glob(f"{directory}/*")

    # result = [os.path.basename(e) for e in result]

    def check_if_workflow_has_yaml(folder):
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith('.yaml'):
                    return True

    for possible_folder in result:
        if check_if_workflow_has_yaml(possible_folder):
            folders.append(os.path.basename(possible_folder))

    return folders


def dict_of_available_workflows():
    """
    looks inside ~/.cloudmesh/workflow directory
    for available workflows and returns them
    as initialized workflows inside a dict
    :return: available workflows as dict
    :rtype: dict
    """
    list_of_workflows = []
    dict_of_workflow_dicts = {}
    folders = get_available_workflows()

    for workflow in folders:
        list_of_workflows.append(load_workflow(name=workflow))
    for workflow in list_of_workflows:
        dict_of_workflow_dicts[workflow.name] = workflow.dict_of_workflow
    return dict_of_workflow_dicts


class Jobpy(BaseModel):
    name: str
    user: str
    host: str
    label: str | None = None
    kind: str | None = None
    status: str | None = None
    progress: int | None = None
    script: str | None = None
    pid: int | None = None
    parent: str | None = None


# q = test_run()

app = FastAPI(title="cloudmesh-cc", version=cm_version)

#
# REGISTER template and static dir
#

static_dir = pkg_resources.resource_filename("cloudmesh.cc", "service/static")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

template_dir = pkg_resources.resource_filename("cloudmesh.cc", "service/templates")
templates = Jinja2Templates(directory=template_dir)

www_dir = pkg_resources.resource_filename("cloudmesh.cc", "www")
www = Jinja2Templates(directory=www_dir)


#
# ROUTES
#


def load_workflow(name: str, load_with_graph=False, load=True) -> Workflow:
    """
    loads a workflow corresponding to given name

    :param name: name of workflow
    :type name: str
    :param load_with_graph:
    :type load_with_graph:
    :param load:
    :type load:
    :return: loaded workflow
    :rtype: Workflow
    """
    filename = Shell.map_filename(f"~/.cloudmesh/workflow/{name}/{name}.yaml").path
    w = Workflow(filename=filename, load=load)
    # w.__init__(filename=filename)
    # w.load(filename=filename)
    if load_with_graph:
        pass
        # w.graph.save_to_file(filename=f"{name}.svg")
    # w.load(filename)
    # print(w.yaml)
    return w


async def image_watcher(request, name_of_workflow: str):
    """
    watches an svg for changes

    :param name_of_workflow: name of workflow to get svg for
    :type name_of_workflow: str
    :return: svg as text form
    :rtype: str
    """
    interval = 0.2

    filename = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/{name_of_workflow}.yaml').path
    w = load_workflow(name=name_of_workflow, load_with_graph=True)
    w.graph.load(filename=filename)
    svg_file = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/{name_of_workflow}.svg').path
    w.graph.save(filename=svg_file, colors="status",
                 layout=nx.circular_layout, engine="dot")

    runtime_graph_file = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/runtime/{name_of_workflow}.svg'
    ).path
    if not os.path.isfile(runtime_graph_file):
        Shell.copy(svg_file, runtime_graph_file)

    placeholder_timestamp = None
    svg = ''
    while True:
        if await request.is_disconnected():
            print('disconnected')
            break
        current_timestamp = os.stat(runtime_graph_file).st_mtime
        if current_timestamp != placeholder_timestamp:
            placeholder_timestamp = current_timestamp
            try:
                svg = '\n'.join(
                    Shell.find_lines_between(readfile(runtime_graph_file).splitlines(),
                                             r'<svg',
                                             r'</svg>'))
            except:  # noqa: E722
                pass
            yield svg
        time.sleep(interval)


def penultimate_status_watcher(request, name_of_workflow: str):
    """
    watches a runtime yaml for status changes

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve statuses for
    :type name_of_workflow: str
    :return: dictionary/Counter of statuses
    :rtype: dict
    """
    interval = 0.2

    runtime_yaml = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/runtime/{name_of_workflow}.yaml').path
    original_yaml = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/{name_of_workflow}.yaml').path
    if not os.path.isfile(runtime_yaml):
        Shell.copy(original_yaml, runtime_yaml)

    runtime_dict = yaml.safe_load(Path(runtime_yaml).read_text())
    states = []
    for state in ['done', 'ready', 'failed', 'submitted', 'running']:
        states.append(state)
    if runtime_dict is None:
        return None
    for name in runtime_dict['workflow']['nodes']:  # ?
        states.append(runtime_dict['workflow']['nodes'][name]["status"])

    count = Counter(states)
    for state in ['done', 'ready', 'failed', 'submitted', 'running']:
        count[state] = count[state] - 1
    return count


async def datatable_server(request, name_of_workflow: str):
    """
    server side event watcher that returns datatable when changes are detected

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve datatable for
    :type name_of_workflow: str
    :return: the datatable as html
    :rtype: str
    """
    interval = 0.2
    runtime_yaml_filepath = path_expand(
        f'~/.cloudmesh/workflow/{name_of_workflow}/runtime/{name_of_workflow}.yaml')
    original_yaml_filepath = path_expand(
        f'~/.cloudmesh/workflow/{name_of_workflow}/{name_of_workflow}.yaml')

    # w = load_workflow(name_of_workflow)
    # w.create_topological_order()

    def runtime_dict_getter():

        runtime_yaml_to_read = readfile(runtime_yaml_filepath)
        original_yaml_to_read = readfile(original_yaml_filepath)

        runtime_yaml_file = yaml.safe_load(runtime_yaml_to_read)
        original_yaml_file = yaml.safe_load(original_yaml_to_read)

        # we must delete the job names that are merely expanded dependencies
        for job_name in list(runtime_yaml_file['workflow']['nodes'].keys()):
            # print(node_name)
            # print(w.graph.nodes.keys())
            if job_name not in original_yaml_file['workflow']['nodes']:
                del runtime_yaml_file['workflow']['nodes'][job_name]
            # else:
            #    runtime_yaml_file['workflow']['nodes'][job_name]['no'] = dict_with_order['nodes'][job_name]['no']
        # banner(str(w.graph.nodes[job_name]['progress']))
        # pprint.pprint(w.graph.nodes)

        dictionary = runtime_yaml_file['workflow']['nodes']
        table_html_template = \
            fr"""
            <table id="example" class="display" style="width:100%">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Host</th>
                        <th>Progress</th>
                        <th>Script</th>
                    </tr>
                </thead>
                <tbody>
            """
        for job, items in dictionary.items():
            table_html_template += \
                fr"""
                    <tr>
                        <td>{items['number']}</td>
                        <td>{job}</td>
                        <td>{items['status']}</td>
                        <td>{items['host']}</td>
                        <td>{items['progress']}&nbsp;<progress value="{items['progress']}" max="100"></progress></td>
                        <td>{items['script']}</td>
                    </tr>
                """
        table_html_template += \
            r"""
                </tbody>
                <tfoot>
                    <tr>
                    </tr>
                </tfoot>
            </table>
        """
        return table_html_template

    placeholder_dict = None
    while True:
        if await request.is_disconnected():
            print('disconnected')
            break
        current_workflow_dict = yaml.safe_load(readfile(runtime_yaml_filepath))
        if current_workflow_dict != placeholder_dict:
            placeholder_dict = current_workflow_dict
            html_to_return = runtime_dict_getter()
            yield html_to_return
        time.sleep(interval)


async def done_watcher(request, name_of_workflow: str):
    """
    server side event watcher that yields number of jobs that are done

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve done count
    :type name_of_workflow: str
    :return: number of jobs done
    """
    interval = 0.05
    placeholder_status_count = None
    while True:
        count = penultimate_status_watcher(request,
                                           name_of_workflow=name_of_workflow)
        if await request.is_disconnected():
            print('disconnected')
            break
        current_done_count = count['done']
        status_dict = count
        if current_done_count != placeholder_status_count:
            placeholder_status_count = current_done_count
            yield current_done_count

        time.sleep(interval)


async def ready_watcher(request, name_of_workflow: str):
    """
    server side event watcher that yields number of jobs that are ready

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve ready count
    :type name_of_workflow: str
    :return: number of jobs ready
    """
    interval = 0.05
    placeholder_status_count = None
    while True:
        count = penultimate_status_watcher(request,
                                           name_of_workflow=name_of_workflow)
        if await request.is_disconnected():
            print('disconnected')
            break
        current_ready_count = count['ready']
        status_dict = count
        if current_ready_count != placeholder_status_count:
            placeholder_status_count = current_ready_count
            yield current_ready_count

        time.sleep(interval)


async def failed_watcher(request, name_of_workflow: str):
    """
    server side event watcher that yields number of jobs that are failed

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve failed count
    :type name_of_workflow: str
    :return: number of jobs failed
    """
    interval = 0.05
    placeholder_status_count = None
    while True:
        count = penultimate_status_watcher(request,
                                           name_of_workflow=name_of_workflow)
        if await request.is_disconnected():
            print('disconnected')
            break
        current_failed_count = count['failed']
        status_dict = count
        if current_failed_count != placeholder_status_count:
            placeholder_status_count = current_failed_count
            yield current_failed_count

        time.sleep(interval)


async def submitted_watcher(request, name_of_workflow: str):
    """
    server side event watcher that yields number of jobs that are submitted

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve submitted count
    :type name_of_workflow: str
    :return: number of jobs submitted
    """
    interval = 0.05
    placeholder_status_count = None
    while True:
        count = penultimate_status_watcher(request,
                                           name_of_workflow=name_of_workflow)
        if await request.is_disconnected():
            print('disconnected')
            break
        current_submitted_count = count['submitted']
        status_dict = count
        if current_submitted_count != placeholder_status_count:
            placeholder_status_count = current_submitted_count
            yield current_submitted_count

        time.sleep(interval)


async def running_watcher(request, name_of_workflow: str):
    """
    server side event watcher that yields number of jobs that are running

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name_of_workflow: name of workflow to retrieve running count
    :type name_of_workflow: str
    :return: number of jobs running
    """
    interval = 0.05
    placeholder_status_count = None
    while True:
        count = penultimate_status_watcher(request,
                                           name_of_workflow=name_of_workflow)
        if await request.is_disconnected():
            print('disconnected')
            break
        current_running_count = count['running']
        status_dict = count
        if current_running_count != placeholder_status_count:
            placeholder_status_count = current_running_count
            yield current_running_count

        time.sleep(interval)


def status_returner(name_of_workflow: str):
    """
    reads a runtime yaml file to return a dict of status of jobs.

    :param name_of_workflow:
    :type name_of_workflow:
    :return:
    :rtype:
    """
    runtime_yaml = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/runtime/{name_of_workflow}.yaml').path
    original_yaml = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name_of_workflow}/{name_of_workflow}.yaml').path
    if not os.path.isfile(runtime_yaml):
        Shell.copy(original_yaml, runtime_yaml)
    runtime_dict = yaml.safe_load(Path(runtime_yaml).read_text())

    states = []
    for state in ['done', 'ready', 'failed', 'submitted', 'running']:
        states.append(state)
    for name in runtime_dict['workflow']['nodes']:  # ?
        states.append(runtime_dict['workflow']['nodes'][name]["status"])

    count = Counter(states)
    for state in ['done', 'ready', 'failed', 'submitted', 'running']:
        count[state] = count[state] - 1
    return count


@app.get("/done-count/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_done(request: Request, name: str):
    """
    give the number of done jobs

    **request** (Request) that is supplied when using web interface
    **name** (str) name of workflow
    **return** (EventSourceResponse) event source response for server side event

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of workflow
    :type name: str
    :return: event source response for server side event
    :rtype: EventSourceResponse
    """
    event_generator = done_watcher(request, name)
    return EventSourceResponse(event_generator)


@app.get("/ready-count/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_ready(request: Request, name: str):
    """
    give the number of ready jobs

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of workflow
    :type name: str
    :return: event source response for server side event
    :rtype: EventSourceResponse
    """
    event_generator = ready_watcher(request, name)
    return EventSourceResponse(event_generator)


@app.get("/failed-count/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_failed(request: Request, name: str):
    """
    give the number of failed jobs

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of workflow
    :type name: str
    :return: event source response for server side event
    :rtype: EventSourceResponse
    """
    event_generator = failed_watcher(request, name)
    return EventSourceResponse(event_generator)


@app.get("/submitted-count/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_submitted(request: Request, name: str):
    """
    give the number of submitted jobs

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of workflow
    :type name: str
    :return: event source response for server side event
    :rtype: EventSourceResponse
    """
    event_generator = submitted_watcher(request, name)
    return EventSourceResponse(event_generator)


@app.get("/running-count/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_running(request: Request, name: str):
    """
    give the number of running jobs

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of workflow
    :type name: str
    :return: event source response for server side event
    :rtype: EventSourceResponse
    """
    event_generator = running_watcher(request, name)
    return EventSourceResponse(event_generator)


#
# HOME
#

@app.get("/",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
@app.get("/home",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
async def home_page(request: Request):
    """
    home function that features html and
    sidebar

    :return: up message
    """
    os.path.dirname(__file__)
    os.chdir(os.path.dirname(__file__))
    os.chdir(Path('../../..').as_posix())
    folders = get_available_workflows()
    page = "cloudmesh/cc/service/markdown/home.md"
    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("home.html", {"request": request,
                                                    "workflowlist": folders,
                                                    "html": html})


#
# CONTACT
#

@app.get("/contact",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
async def contact_page(request: Request):
    """
    page that lists contact information

    :return: contact page
    """
    os.path.dirname(__file__)
    os.chdir(os.path.dirname(__file__))
    os.chdir(Path('../../..').as_posix())
    folders = get_available_workflows()
    page = "cloudmesh/cc/service/markdown/contact.md"
    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("contact.html",
                                      {"request": request,
                                       "workflowlist": folders,
                                       "html": html})


@app.get("/manpage",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
async def man_page(request: Request):
    """
    page that lists contact information

    :return: contact page
    """
    os.path.dirname(__file__)
    os.chdir(os.path.dirname(__file__))
    os.chdir(Path('../../..').as_posix())
    folders = get_available_workflows()
    page = "cloudmesh/cc/service/markdown/contact.md"

    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("contact.html",
                                      {"request": request,
                                       "workflowlist": folders,
                                       "html": html})


@app.get("/about",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
async def about_page(request: Request):
    """
    page that lists readme as html

    :return: about page
    """
    os.path.dirname(__file__)
    os.chdir(os.path.dirname(__file__))
    os.chdir(Path('../../..').as_posix())
    page = "cloudmesh/cc/service/markdown/about.md"
    about = readfile(page)
    html = markdown.markdown(about)
    folders = get_available_workflows()
    return templates.TemplateResponse("about.html",
                                      {"request": request,
                                       "html": html,
                                       "workflowlist": folders})


#
# WORKFLOW
#


@app.get("/workflows",
         tags=['workflow'])
def list_workflows(output: str = None):
    """
    returns a list of all workflows found on local computer

    Parameters:

    - **output**: (str) format to print available workflows, which can be
    json, csv, or none which prints it as dict

    :param output: format to print available workflows, which can be
    json, csv, or none which prints it as dict
    :type output: str
    :return: list of workflow names
    """
    """    
    curl -X 'GET' \
        'http://127.0.0.1:8000/workflows' \
        -H 'accept: application/json'
    """

    dict_of_workflow_dicts = dict_of_available_workflows()

    try:

        if output == 'json':
            json_workflow = json.dumps(dict_of_workflow_dicts)
            json_filepath = Shell.map_filename(
                f'~/.cloudmesh/workflow/all-workflows-json.json').path
            writefile(json_filepath, json_workflow)
            return FileResponse(json_filepath)

        elif output == 'csv':
            df = pd.DataFrame(dict_of_workflow_dicts)
            csv_filepath = Shell.map_filename(
                f'~/.cloudmesh/workflow/all-workflows-csv.csv').path

            # stream = io.StringIO()
            response = StreamingResponse(io.StringIO(df.to_csv()),
                                         media_type="text/csv")
            response.headers["Content-Disposition"] = f"attachment; filename=all-workflows-csv.csv"
            return response

        else:
            folders = get_available_workflows()
            return {"workflows": folders}

    except Exception as e:  # noqa: E722
        return {"message": f"No workflows found"}


# we need to be putting in there whatever we need to be updating.
# 1. upload a.yaml (standalone, doesnt need anything else)
# 1.1 upload a.yaml?name=d
# 2. upload b.yaml (contains b.sh, b.ipynb, b.py, and maybe b.data)
# 2.1 upload b.yaml?name=d
# 2.1 this needs a second part - upload b.sh, b.ipynb, b.py, b.data
# 3. upload directory/* (the * represents the yaml and the scripts)
# 3.1 the name is determined from the yaml file in that directory
# 3.2 upload directory?name=d
# the uploaded workflow is called 'd' (placeholder name)
# 4. upload compressed file (tar) the format is tgz,xz (two different formats)
# 4.1 a.tgz and a.xz which contain whatever is being provided in 1,2,3
# 4.2 they are uncompressed just as if they were to do an individual upload.
# name is optional because the name is determined on what is provided
@app.post("/workflow/upload",
          tags=['workflow'])
def upload(directory: str = Query(None,
                                  description='path to workflow dir '
                                              'that contains scripts '
                                              'and yaml file'),
           archive: str = Query(None,
                                description='path to archive file that '
                                            'can be tgx, xz, tar.gz, '
                                            'or tar'),
           yaml: str = Query(None,
                             description='path to yaml file for workflow')):
    """
    upload a workflow to the ~/.cloudmesh/workflow directory for running
    or editing.

    Parameters:

    - **directory**: (str) path to directory with workflow files
    - **archive**: (str) path to archive file, which can be tgx, xz, tar.gz,
    or tar, that contains workflow files
    - **yaml**: (str) path to yaml file that specifies workflow configuration
    """

    """
    :param directory: path to directory with workflow files
    :type directory: str

    curl -X 'POST' \
        'http://127.0.0.1:8000/workflow/upload?directory=~/cm/cloudmesh-cc/tests/workflow-example' \
        -H 'accept: application/json' \
        -d ''

    :param archive: tgz, xz, tar.gz, or tar file with workflow files
    :type archive: str

    curl -X 'POST' \
        'http://127.0.0.1:8000/workflow/upload?archive=ThePathToYourArchiveFile' \
        -H 'accept: application/json' \
        -d ''

    :param yaml: yaml file with workflow specifications
    :type yaml: str

    curl -X 'POST' \
        'http://127.0.0.1:8000/workflow/upload?yaml=~/cm/cloudmesh-cc/tests/workflow-example/workflow-example.yaml' \
        -H 'accept: application/json' \
        -d ''

    :return: success or failure message
    """
    if sum(bool(x) for x in [directory, archive, yaml]) > 1:
        Console.error(f"Only one upload option can be chosen.")
        return {"message": f"Only one upload option can be chosen."}

    elif directory:
        try:
            expanded_dir_path = Path(Shell.map_filename(directory).path).as_posix()
            if not os.path.isdir(expanded_dir_path):
                Console.error(f"{expanded_dir_path} is not a valid dir path")
                return {
                    "message": f"{expanded_dir_path} is not a valid dir path"}
            name = os.path.basename(expanded_dir_path)
            # try:
            #     Shell.run(f'tar -C {expanded_dir_path} -cf {name}.tar .')
            # except Exception as e:
            #     print(e.output)
            # tar_location = Path(
            #     Shell.map_filename(f'./{name}.tar').path).as_posix()
            #
            runtime_directory = Path(path_expand(
                f"~/.cloudmesh/workflow/{name}/runtime/")).as_posix()
            yaml_location = path_expand(
                f"~/.cloudmesh/workflow/{name}/{name}.yaml")
            Shell.mkdir(runtime_directory)
            # command = f'tar --strip-components 1 --force-local -xvf {tar_location} -C {runtime_directory}'
            #
            # print(command)
            # os.system(command)
            # Shell.rm(f'{tar_location}')
            expanded_dir_path = posixpath.join(expanded_dir_path, '')
            # expanded_dir_path = Path(expanded_dir_path).as_posix()

            # these try excepts are needed in the case of a workflow with
            # all py files! or all sh files! or all ipynb files!
            for kind in ["yaml", "sh", "py", "ipynb"]:
                try:
                    Shell.run(f'cp {expanded_dir_path}*.{kind} {runtime_directory}')
                except:  # noqa: E722
                    pass
            runtime_yaml_location = os.path.join(runtime_directory,
                                                 f'{name}.yaml')
            runtime_yaml_location = os.path.normpath(runtime_yaml_location)
            Shell.copy(runtime_yaml_location, yaml_location)
            w = Workflow()
            w.load(filename=runtime_yaml_location)
            print(w.yaml)
            return {
                "message": f"Successfully uploaded {name} dir"}
        except Exception as e:
            Console.error(e, traceflag=True)
            return {"message": f"There was an error uploading the file {e}"}

    elif archive:
        try:
            name = os.path.basename(archive).split('.')[0]
            runtime_directory = path_expand(
                f"~/.cloudmesh/workflow/{name}/runtime/")
            yaml_location = path_expand(
                f"~/.cloudmesh/workflow/{name}/{name}.yaml")
            runtime_directory = Path(runtime_directory).as_posix()
            archive_location = Path(Shell.map_filename(archive).path).as_posix()

            if archive.endswith('.tgz') or \
                    archive.endswith('.xz') or \
                    archive.endswith('.tar.gz') or \
                    archive.endswith('.tar'):

                w = Workflow()
                Shell.mkdir(runtime_directory)
                if archive.endswith('.tar') or archive.endswith('.xz'):
                    command = f'tar --strip-components 1 --force-local -xvf {archive_location} -C {runtime_directory}'
                else:
                    command = f'tar --strip-components 1 --force-local -xvzf {archive_location} -C {runtime_directory}'
                print(command)
                os.system(command)
                runtime_yaml_location = os.path.join(runtime_directory,
                                                     f'{name}.yaml')
                runtime_yaml_location = os.path.normpath(runtime_yaml_location)
                Shell.copy(runtime_yaml_location, yaml_location)
                w.load(filename=runtime_yaml_location)
                print(w.yaml)

                return {"message": f"Successfully uploaded {archive}"}

        except Exception as e:
            Console.error(e, traceflag=True)
            return {"message": f"There was an error uploading the file {e}"}

        # finally:
        #     await file.close()

    elif yaml:
        try:
            if not yaml.endswith('.yaml'):
                raise Exception
            name = os.path.basename(yaml).split('.')[0]
            original_yaml_location = Path(Shell.map_filename(yaml).path).as_posix()
            yaml_location = Path(path_expand(
                f"~/.cloudmesh/workflow/{name}/{name}.yaml")).as_posix()
            runtime_directory = Path(path_expand(
                f"~/.cloudmesh/workflow/{name}/runtime/")).as_posix()
            Shell.mkdir(runtime_directory)

            print("LOG: Create Workflow at:", yaml_location)
            Shell.copy(original_yaml_location, yaml_location)
            w = load_workflow(name)
            print(w.yaml)
            return {"message": f"Successfully uploaded {yaml}"}

        except Exception as e:
            Console.error(e, traceflag=True)
            return {"message": f"There was an error uploading the file {e}"}


# import requests
#
# url = 'http://127.0.0.1:8000/workflow/upload'
# file = {'file': open('images/1.png', 'rb')}
# resp = requests.post(url=url, files=file)
# print(resp.json())

@app.get("/delete/{name}",
         tags=['workflow'],
         include_in_schema=include_portal_tag_in_schema)
def delete_workflow_direct_url(name: str):
    """
    :param name: name of workflow
    :type name: str

    :return:
    :rtype:
    """
    try:
        # w = load_workflow(name)
        directory = path_expand(f"~/.cloudmesh/workflow/{name}")
        os.system(f"rm -rf {directory}")
        return RedirectResponse(url=f'/home')
    except Exception as e:
        Console.error(e, traceflag=True)
        return {
            "message": f"There was an error deleting the workflow '{name}'"}


@app.delete("/workflow/{name}",
            tags=['workflow'])
def delete_workflow(name: str, job: str = None):
    """
    deletes an entire workflow. if the job is specified, then deletes
    just the job in the workflow.

    Parameters:

    - **name**: (str) name of workflow to delete
    - **job**: (str) name of job to delete in a workflow, if specified
    """
    """

    example curl:
    we need to have first uploaded workflow-example for this curl to work!
    curl -X 'DELETE' \
        'http://127.0.0.1:8000/workflow/workflow-example' \
        -H 'accept: application/json'

    :param name: name of the workflow
    :type name: str
    :param job: name of the job
    :type job: str
    :return: success or failure message
    """
    if job is not None:
        # if we specify to delete the job
        try:
            w = load_workflow(name)
            # print(w[job])
            w.remove_job(job, state=True)
            return {"message": f"The job {job} was deleted in the workflow {name}"}
        except Exception as e:
            print(e)
            Console.error(e, traceflag=True)
            return {"message": f"There was an error deleting the job '{job}' in workflow '{name}'"}
    else:
        # if we specify to delete the workflow
        try:
            # w = load_workflow(name)
            directory = path_expand(f"~/.cloudmesh/workflow/{name}")
            os.system(f"rm -rf {directory}")
            return {"message": f"The workflow {name} was deleted and the directory {directory} was removed"}
        except Exception as e:
            Console.error(e, traceflag=True)
            return {"message": f"There was an error deleting the workflow '{name}'"}


@app.get("/edit/{name}",
         tags=['workflow'],
         status_code=204,
         response_class=Response,
         include_in_schema=include_portal_tag_in_schema)
def edit_workflow_direct_url(name: str):
    """
    :param name: name of workflow
    :type name: str
    :return:
    :rtype:
    """
    try:
        # w = load_workflow(name)
        yaml_file = path_expand(f"~/.cloudmesh/workflow/{name}/{name}.yaml")
        os.system(f"emacs {yaml_file}")
    except Exception as e:
        Console.error(e, traceflag=True)
        return {
            "message": f"There was an error deleting the workflow '{name}'"}


@app.get("/workflow/{name}",
         tags=['workflow'])
def get_workflow(request: Request,
                 name: str,
                 job: str = None,
                 output: str = None):
    """
    retrieves a workflow by its name. if the job is specified, retrieves
    just the job in the specified workflow

    Parameters:

    - **name**: (str) name of workflow to retrieve
    - **job**: (str) name of job to retrieve, if specified (optional)
    - **output**: (str) how to print workflow, which can be
    html, graph, json, table, or csv. if not specified, then returned as dict
    """
    """

    you need to have first uploaded the workflow-example for this curl to work!
    curl -X 'GET' \
        'http://127.0.0.1:8000/workflow/workflow-example' \
        -H 'accept: application/json'

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of the workflow
    :type name: str
    :param job: name of the job
    :type job: str
    :param output: how to print workflow. can be html or table
    :type output: str
    :return: success or failure message
    :rtype: dict

    """
    try:
        if output == 'html':
            # #result = [os.path.basename(e) for e in result]
            # w = load_workflow(name=name, load_with_graph=True)
            # print(w.dict_of_workflow)
            # df = pd.DataFrame(w.dict_of_workflow)
            # df_html = df.to_html()
            # #html_workflow = Printer.write(table=w_dict, output='html')
            # script_dir = os.path.dirname(os.path.realpath(__file__))
            # script_dir = os.path.join(script_dir, 'templates')
            # script_dir = os.path.join(script_dir, f'{name}-html.html')
            # writefile(script_dir, df_html)
            # return templates.TemplateResponse(f"{name}-html.html", {"request": request})
            w = load_workflow(name=name, load_with_graph=True)
            test = w.table
            data = dict(w.graph.nodes)
            order = ['number',
                     'host',
                     'status',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']
            workflow_html = Printer.dict_html(w.graph.nodes, order=order)
            script_dir = os.path.dirname(os.path.realpath(__file__))
            script_dir = os.path.join(script_dir, 'templates')
            script_dir = os.path.join(script_dir, f'{name}-html.html')
            writefile(script_dir, workflow_html)
            return templates.TemplateResponse(f"{name}-html.html", {"request": request})

        elif output == 'graph':
            runtime_svg = Shell.map_filename(f'~/.cloudmesh/workflow/{name}/runtime/{name}.svg').path
            if os.path.isfile(runtime_svg):
                return FileResponse(runtime_svg)
            filename = Shell.map_filename(
                f'~/.cloudmesh/workflow/{name}/{name}.yaml').path
            w = load_workflow(name=name, load_with_graph=True)
            w.graph.load(filename=filename)
            svg_file = Shell.map_filename(
                f'~/.cloudmesh/workflow/{name}/{name}.svg').path
            w.graph.save(filename=svg_file, colors="status",
                         layout=nx.circular_layout, engine="dot")
            print(w.graph)
            print(w.table)

            return FileResponse(svg_file)

        elif output == 'json':
            w = load_workflow(name)
            w_dict = w.dict_of_workflow
            json_workflow = json.dumps(w_dict)
            json_filepath = Shell.map_filename(f'~/.cloudmesh/workflow/{name}/{name}-json.json').path
            writefile(json_filepath, json_workflow)
            return FileResponse(json_filepath)

        elif output == 'table':
            folders = get_available_workflows()
            # we must initialize preferences in case they do not exist
            configuration_file = Shell.map_filename(
                '~/.cloudmesh/workflow/table-preferences.yaml').path
            if not os.path.isfile(configuration_file):
                table_preferences = {
                    'id': True,
                    'name': True,
                    'status': True,
                    'host': True,
                    'progress': True,
                    'script': True
                }
                with open(configuration_file, 'w') as f:
                    yaml.dump(table_preferences, f, default_flow_style=False,
                              sort_keys=False)
            w = load_workflow(name)

            order = ['number',
                     'host',
                     'status',
                     'name',
                     'progress',
                     'script',
                     'user',
                     'parent',
                     'kind']

            w.create_topological_order()

            # this following line temporarily causes the web table
            # view to show incorrect job status values, because the
            # yaml is completely overwritten. this can be improved
            # by only writing the number values to runtime filename yaml.
            # not implemented...
            w.graph.save_to_yaml(w.runtime_filename)
            workflow_dict = Printer.dict(w.graph.nodes, order=order)

            configuration_file = Shell.map_filename(
                '~/.cloudmesh/workflow/table-preferences.yaml').path
            preferences = {'id': True, 'name': True, 'progress': True,
                           'status': True}
            if os.path.isfile(configuration_file):
                preferences = yaml.safe_load(
                    Path(configuration_file).read_text())

            return templates.TemplateResponse("workflow-table.html",
                                              {"request": request,
                                               "name_of_workflow": name,
                                               "workflowlist": folders,
                                               "preferences": preferences})

        elif output == 'csv':
            w = load_workflow(name)
            w_dict = w.dict_of_workflow
            df = pd.DataFrame(w_dict)
            response = StreamingResponse(io.StringIO(df.to_csv()),
                                         media_type="text/csv")

            response.headers["Content-Disposition"] = f"attachment; filename={name}-csv.csv"
            return response

    except Exception as e:
        print(e)
        Console.error(e, traceflag=True)
        return {"message": f"There was an error with getting the workflow '{name}'"}

    if job is not None:
        try:
            w = load_workflow(name)
            result = w[job]
            return {name: result}
        except Exception as e:
            print(e)
            Console.error(e, traceflag=True)
            return {"message": f"There was an error with getting the job '{job}' in workflow '{name}'"}
    else:
        try:
            w = load_workflow(name)
            return {name: w}
        except Exception as e:
            print(e)
            Console.error(e, traceflag=True)
            return {"message": f"There was an error with getting the workflow '{name}'"}


@app.get("/workflow-graph/{name}",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
def get_workflow_graph(request: Request, name: str):
    """
    see the graph embedded within web interface

    :param request: request that is supplied when using web interface
    :type request: Request
    :param name: name of workflow to retrieve the graph for
    :type name: str
    :return: html page with graph
    """
    # folders = get_available_workflows()
    # svg = f"http://127.0.0.1:8000/workflow/{name}?output=graph"
    # import requests
    # r = requests.get(svg)
    # # r = '''
    # # <ul>
    # #     <li>
    # #         hello
    # #     </li>
    # # </ul>
    # # '''
    #
    # print(r.text)
    # w = load_workflow(name)
    # status_dict = w.analyze_states()
    # return templates.TemplateResponse("workflow-graph.html",
    #                                   {"request": request,
    #                                    "svg": r.text,
    #                                    "name_of_workflow": name,
    #                                    "workflowlist": folders,
    #                                    "status_dict": status_dict})
    event_generator = image_watcher(request, name)
    return EventSourceResponse(event_generator)


@app.get("/watcher/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_watcher(request: Request, name: str):
    """

    :param request:
    :type request:
    :param name: name of workflow
    :type name: str
    :return:
    :rtype:
    """
    folders = get_available_workflows()
    # w = load_workflow(name)
    return templates.TemplateResponse("watcher.html",
                                      {"request": request,
                                       "name": name,
                                       "workflowlist": folders})


@app.get("/serve-datatable/{name}",
         include_in_schema=include_portal_tag_in_schema)
def serve_table(request: Request, name: str):
    """

    :param request:
    :type request:
    :param name: name of workflow
    :type name: str
    :return:
    :rtype:
    """
    event_generator = datatable_server(request, name)
    return EventSourceResponse(event_generator)


@app.get("/workflow/run/{name}",
         tags=['workflow'])
def run_workflow(name: str,
                 run_type: str = "topo",
                 redirect: str = None,
                 show: bool = False):
    """
    runs a specified workflow according to provided run type

    Parameters:

    - **name**: (str) name of workflow to run
    - **run_type**: (str) how to run workflow. only topo is implemented
    (topological sort of jobs)
    - **redirect**: (str) where to redirect after initializing the run.
    only graph is implemented for web interface. None will disable redirect
    - **show**: (bool) whether to show the graph as the workflow is run
    """
    """
    example curl:
    we need to have first uploaded workflow-example for this curl to work!
    curl -X 'GET' \
        'http://127.0.0.1:8000/workflow/run/workflow-example?run_type=topo' \
        -H 'accept: application/json'

    :param name: name of workflow
    :type name: str
    :param run_type: type of run, either topo or parallel
    :type run_type: str
    :param redirect: where to redirect after initiating run
    :type redirect: str
    :param show: whether to display the graph as the workflow runs
    :type show: bool
    :return: success or exception message
    :rtype:
    """
    # reset the yaml and the log files
    workflow_runtime_dir = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name}/runtime').path
    workflow_runtime_star = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name}/runtime/*').path
    workflow_dir = Shell.map_filename(
        f'~/.cloudmesh/workflow/{name}/').path
    if os.path.isdir(workflow_runtime_dir):
        files = glob.glob(workflow_runtime_star)
        for file in files:
            if file.endswith(".yaml") or file.endswith(".log"):
                os.remove(file)
        files2 = glob.glob(workflow_dir)
        for file in files2:
            if file.endswith(".yaml"):
                Shell.copy(file, workflow_runtime_dir)

    w = load_workflow(name)
    w.create_topological_order()
    os.chdir(os.path.dirname(w.filename))

    try:
        if run_type == "topo":
            threading.Thread(
                target=w.run_topo, kwargs={'show': show}).start()
            # w.run_topo(show=True)
        else:
            threading.Thread(
                target=w.run_parallel, kwargs={'show': show}).start()
            # w.run_parallel(show=True)
        # return {"Success": "Workflow ran successfully"}
        if redirect == 'graph':
            return RedirectResponse(url=f'/watcher/{w.name}')
        return RedirectResponse(url=f'/workflow-running/{w.name}')
    except Exception as e:
        print("Exception:", e)


@app.get("/workflow-running/{name}",
         tags=['portal'],
         include_in_schema=include_portal_tag_in_schema)
def watch_running_workflow(request: Request,
                           name: str):
    """
    page for watching a workflow that has been started

    :param request: type of request (api does this automatically in browser)
    :type request: Request
    :param name: name of workflow
    :type name: str
    :return: html page with updating table
    """

    folders = get_available_workflows()

    runtime_yaml_filepath = path_expand(
        f'~/.cloudmesh/workflow/{name}/runtime/{name}.yaml')
    original_yaml_filepath = path_expand(
        f'~/.cloudmesh/workflow/{name}/{name}.yaml')

    runtime_yaml_to_read = readfile(runtime_yaml_filepath)
    original_yaml_to_read = readfile(original_yaml_filepath)

    runtime_yaml_file = yaml.safe_load(runtime_yaml_to_read)
    original_yaml_file = yaml.safe_load(original_yaml_to_read)

    # we must delete the job names that are merely expanded dependencies
    for job_name in list(runtime_yaml_file['workflow']['nodes'].keys()):
        # print(node_name)
        # print(w.graph.nodes.keys())
        if job_name not in original_yaml_file['workflow']['nodes']:
            del runtime_yaml_file['workflow']['nodes'][job_name]
        # else:
        #    runtime_yaml_file['workflow']['nodes'][job_name]['no'] = dict_with_order['nodes'][job_name]['no']
    # banner(str(w.graph.nodes[job_name]['progress']))
    # pprint.pprint(w.graph.nodes)

    # pprint(runtime_yaml_file['workflow']['nodes'])

    configuration_file = Shell.map_filename(
        '~/.cloudmesh/workflow/table-preferences.yaml').path
    preferences = {'id': True, 'name': True, 'status': True, 'host': True,
                   'progress': True, 'script': True}
    if os.path.isfile(configuration_file):
        preferences = yaml.safe_load(
            Path(configuration_file).read_text())

    return templates.TemplateResponse("workflow-running.html",
                                      {"request": request,
                                       "dictionary": runtime_yaml_file['workflow']['nodes'],
                                       "name_of_workflow": name,
                                       "workflowlist": folders,
                                       "preferences": preferences})


@app.get("/workflow/job/{name_of_workflow}",
         tags=['workflow'])
def add_job(name_of_workflow: str,
            job: str,
            user: str = None,
            host: str = None,
            kind: str = None,
            status: str = None,
            script: str = None,
            exec: str = None,
            progress: str = None,
            label: str = None,
            parent: str = None):
    """
    adds a node/job to a workflow

    A check
    is returned and the user is alerted if arguments are missing
    arguments are passed in ATTRIBUTE=VALUE fashion.
    if the name of the workflow is omitted, the default workflow is used.
    If no job name is specified, an automated number that is kept in the
    config.yaml file will be used and the name will be job-n

    Parameters:

    - **name_of_workflow**: (str) the name of workflow
    - **job**: (str) the name of the job to add
    - **user**: (str) name of user of the job
    - **host**: (str) name of the host of the job
    - **kind**: (str) the kind of job, like ssh, slurm, local,
    - **status**: (str) the status of the job, such as ready,
    - **script**: (str) the name of the script to be run,
    including file extension
    - **exec**: (str) command(s) to execute
    - **progress**: (str) value of job progress from 0 to 100
    - **label**: (str) text to be shown on node in the graph
    - **parent**: (str) parent job
    """
    """
    **Example curl Script**

    We need to have first uploaded workflow-example for this curl to work:

    curl -X 'GET' \
        'http://127.0.0.1:8000/add-job/workflow-example?job=myJob&user=aPerson&host=local&kind=local&status=ready&script=aJob.sh&progress=0&label=aLabel' \
        -H 'accept: application/json'
    
    :param name_of_workflow: the name of the workflow
    :type name_of_workflow: str
    :param job: the name of the job
    :type job: str
    :param user: name of user of the job
    :type user: str
    :param host: name of the host of the job
    :type host: str
    :param kind: the kind of job, like ssh, slurm, local
    :type kind: str
    :param status: the status of the job, such as ready
    :type status: str
    :param script: the name of the script to be run, including file extension
    :type script: str
    :param exec: command(s) to execute
    :type exec: str
    :param progress: value of job progress from 0 to 100
    :type progress: str
    :param label: text to be shown on node in the graph
    :type label: str
    :param parent: parent job
    :type parent: str
    :return: returns jobs within the specified workflow
    :rtype: dict
    """

    # cms cc workflow service add [--name=NAME] --job=JOB ARGS...
    # cms cc workflow service add --name=workflow --job=c user=gregor host=localhost kind=local status=ready script=c.sh
    # curl -X 'POST' 'http://127.0.0.1:8000/workflow/workflow?job=c&user=gregor&host=localhost&kind=local&status=ready&script=c.sh' -H 'accept: application/json'
    w = load_workflow(name=name_of_workflow)

    try:
        if type(progress) == str:
            progress = int(progress)
        w.add_job(filename=w.filename,
                  name=job,
                  user=user,
                  host=host,
                  label=label,
                  kind=kind,
                  status=status,
                  progress=progress,
                  script=script)
        if parent:
            w.add_dependencies(f"{parent},{job}")
        w.save_with_state(w.filename)
        w.save(w.filename)
    except Exception as e:
        print("Exception:", e)

    return {"jobs": w.jobs}


@app.get('/preferences',
         include_in_schema=include_portal_tag_in_schema)
def preferences_post(request: Request):
    """
    preferences page

    :param request:
    :type request:

    :return: preferences page
    """
    folders = get_available_workflows()
    # read this from configuration file
    configuration_file = Shell.map_filename(
        '~/.cloudmesh/workflow/table-preferences.yaml').path
    preferences = {'id': True, 'name': True, 'status': True, 'host': True,
                   'progress': True, 'script': True}
    if os.path.isfile(configuration_file):
        preferences = yaml.safe_load(Path(configuration_file).read_text())
    # for key, value in preferences.items():
    # if value:
    # value = 'checked'
    # page = "cloudmesh/cc/service/markdown/contact.md"
    # import markdown
    # contact = readfile(page)
    # html = markdown.markdown(contact)
    r = templates.TemplateResponse("preferences.html",
                                   {"request": request,
                                    "workflowlist": folders,
                                    "preferences": preferences})
    pprint(r)
    return r


@app.post('/preferences',
          status_code=204,
          response_class=Response,
          include_in_schema=include_portal_tag_in_schema)
def preferences_post(request: Request,
                     id: bool = Form(False),
                     name: bool = Form(False),
                     status: bool = Form(False),
                     host: bool = Form(False),
                     progress: bool = Form(False),
                     script: bool = Form(False)):
    """

    :param request:
    :type request:
    :param id:
    :type id:
    :param name: Name of the Workflow
    :type name: str
    :param status:
    :type status:
    :param host:
    :type host:
    :param progress:
    :type progress:
    :param script:
    :type script:
    :return:
    :rtype:
    """
    folders = get_available_workflows()
    # print(preferences)
    table_preferences = {
        'id': id,
        'name': name,
        'status': status,
        'host': host,
        'progress': progress,
        'script': script
    }
    dot_cloudmesh_dir = Shell.map_filename('~/.cloudmesh/workflow').path
    configuration_file = Shell.map_filename(
        '~/.cloudmesh/workflow/table-preferences.yaml').path
    if not os.path.isdir(dot_cloudmesh_dir):
        Shell.mkdir(dot_cloudmesh_dir)
    # if not os.path.isfile(configuration_file):
    with open(configuration_file, 'w') as f:
        yaml.dump(table_preferences, f, default_flow_style=False,
                  sort_keys=False)


@app.get('/generate-example',
         status_code=302,
         response_class=RedirectResponse,
         include_in_schema=include_portal_tag_in_schema)
def generate_example_workflow(request: Request):
    """
    create example workflow for testing

    :param request: request that is supplied when using web interface
    :type request: Request
    :return: failure message or a redirection to homepage upon success
    :rtype: dict or RedirectResponse
    """
    workflow_example_dir = Shell.map_filename(
        '~/.cloudmesh/workflow/workflow-example').path
    if os.path.isdir(workflow_example_dir):
        Shell.rmdir(workflow_example_dir)
    service_file = Path(f'{__file__}').as_posix()
    service_dir = Path(os.path.dirname(service_file)).as_posix()
    cc_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(service_dir)))).as_posix()
    test_example_dir = Path(f'{cc_dir}/tests/workflow-example/').as_posix()
    expanded_dir_path = Path(Shell.map_filename(test_example_dir).path).as_posix()
    print(expanded_dir_path)
    if not os.path.isdir(expanded_dir_path):
        Console.error(f"{expanded_dir_path} is not a valid dir path")
        return {
            "message": f"{expanded_dir_path} is not a valid dir path"}
    name = os.path.basename(expanded_dir_path)
    # try:
    #     Shell.run(f'tar -C {expanded_dir_path} -cf {name}.tar .')
    # except Exception as e:
    #     print(e.output)
    # tar_location = Path(
    #     Shell.map_filename(f'./{name}.tar').path).as_posix()
    #
    runtime_directory = Path(path_expand(
        f"~/.cloudmesh/workflow/{name}/runtime/")).as_posix()
    yaml_location = path_expand(
        f"~/.cloudmesh/workflow/{name}/{name}.yaml")
    Shell.mkdir(runtime_directory)
    expanded_dir_path = posixpath.join(expanded_dir_path, '')
    # expanded_dir_path = Path(expanded_dir_path).as_posix()

    # these try excepts are needed in the case of a workflow with
    # all py files! or all sh files! or all ipynb files!
    for dirpath, dirnames, filenames in os.walk(expanded_dir_path):
        for filename in filenames:
            if filename.endswith('.yaml') or filename.endswith('.sh') or \
                    filename.endswith('.py') or filename.endswith('.ipynb'):
                Shell.copy(os.path.join(expanded_dir_path, filename), runtime_directory)

    runtime_yaml_location = os.path.join(runtime_directory,
                                         f'{name}.yaml')
    runtime_yaml_location = os.path.normpath(runtime_yaml_location)
    Shell.copy(runtime_yaml_location, yaml_location)
    w = Workflow()
    w.load(filename=runtime_yaml_location)
    print(w.yaml)
    return RedirectResponse('/home', status_code=302)


