import posixpath
import yaml
import logging
import threading
from typing import List, Optional
import networkx as nx
from pathlib import Path

from cloudmesh.cc.queue import Queues
from cloudmesh.cc.workflow import Workflow
from cloudmesh.common import dotdict
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI, Query
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form
from fastapi import File
from fastapi import UploadFile
from fastapi.responses import FileResponse, StreamingResponse, RedirectResponse, Response
from pydantic import BaseModel

from cloudmesh.cc.__version__ import version as cm_version

from fastapi.staticfiles import StaticFiles
import pkg_resources
from cloudmesh.common.console import Console
import os
import io
from cloudmesh.common.util import path_expand
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import writefile, readfile
from cloudmesh.common.util import banner
import pandas as pd
import glob
import json

"""
all the URLs.
@app.get("/", tags=['workflow'])
@app.get("/workflows", tags=['workflow'])
    ?json
    ?yaml
    ?html
    ?dict
    
@app.post("/upload", tags=['workflow'])
@app.delete("/workflow/{name}", tags=['workflow'])
@app.get("/workflow/{name}", tags=['workflow'])
@app.get("/run/{name}", tags=['workflow'])
@app.post("/workflow/{name}", tags=['workflow'])
"""

from cloudmesh.common.variables import Variables
variables = Variables()

debug = variables['debug']
debug = False
debug = True


#
# set if portal routs shoudl be displayed in teh documentation
#
include_in_schema_portal_tag=debug
include_in_schema_portal_tag=False


def test_run():
    """
    creates a test queue with several different jobs
    :return: Queues object
    :rtype: Queues
    """
    kind = 'yamldb'
    q = Queues(filename='~/.cloudmesh/queue/queuetest1')
    q.create(name='local')
    q.create(name='rivanna')
    q.add(name='local', job='job01', command='pwd')
    q.add(name='local', job='job02', command='ls')
    q.add(name='local', job='job03', command='hostname')
    q.add(name='rivanna', job='job04', command='pwd')
    q.add(name='rivanna', job='job05', command='ls - a')
    q.add(name='rivanna', job='job06', command='hostname')
    q.add(name='rivanna', job='job07', command='git status')
    return q


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


q = test_run()

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

# # deprecated only here as example/test once working example is implemented, remove
# @app.get("/item/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     global q
#     jobs = []
#     for queue in q.queues:
#         for job in q.queues[queue]:
#             jobs.append(q.queues[queue][job])
#     order = q.queues[queue][job].keys()
#     order = [word.capitalize() for word in order]
#     Console.error(str(order))
#
#     return templates.TemplateResponse("templates/item.html",
#                                       {"request": request,
#                                        "id": id,
#                                        "jobs": jobs,
#                                        "order": order})
#
# # deprecated only here as example/test once working example is implemented, remove
# @app.get("/items", response_class=HTMLResponse)
# async def item_table(request: Request):
#     return templates.TemplateResponse("templates/table.html",
#                                       {"request": request})

def load_workflow(name: str, load_with_graph=False, load=True) -> Workflow:
    """
    loads a workflow corresponding to given name
    :param name: name of workflow
    :type name: str
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


#
# HOME
#

@app.get("/", tags=['portal'], include_in_schema=include_in_schema_portal_tag)
@app.get("/home", tags=['portal'], include_in_schema=include_in_schema_portal_tag)
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
    import markdown
    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("home.html", {"request": request,
                                                    "workflowlist": folders,
                                                    "html": html})


#
# CONTACT
#

@app.get("/contact", tags=['portal'], include_in_schema=include_in_schema_portal_tag)
async def contact_page(request: Request):
    """
    page that lists contact information
    :return: contact page
    """
    folders = get_available_workflows()
    page = "cloudmesh/cc/service/markdown/contact.md"
    import markdown
    contact = readfile(page)
    html = markdown.markdown(contact)
    return templates.TemplateResponse("contact.html",
                                      {"request": request,
                                       "workflowlist": folders,
                                       "html": html})


@app.get("/about", tags=['portal'], include_in_schema=include_in_schema_portal_tag)
async def about_page(request: Request):
    """
    page that lists readme as html
    :return: about page
    """
    page = "cloudmesh/cc/service/markdown/about.md"
    import requests
    import markdown
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


@app.get("/workflows", tags=['workflow'])
def list_workflows(request: Request, output: str = None):
    """
    This command returns a list of workflows that is found within
    the server.
    curl -X 'GET' \
        'http://127.0.0.1:8000/workflows' \
        -H 'accept: application/json'
    :return: list of workflow names
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

    except Exception as e:
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
@app.post("/upload", tags=['workflow'])
def upload(directory: str = Query(None,
                                        description='path to workflow dir '
                                                    'that contains scripts '
                                                    'and yaml file'),
                 archive: str = Query(None,
                                      description='can be tgx, xz, tar.gz, '
                                                  'or tar'),
                 yaml: str = Query(None,
                                   description='yaml file for workflow')):
    """
    upload a workflow to the ~/.cloudmesh/workflow directory for running
    or editing.
    :param directory: path to directory with workflow files
    :type directory: str
    curl -X 'POST' \
        'http://127.0.0.1:8000/upload?directory=~/cm/cloudmesh-cc/tests/workflow-example' \
        -H 'accept: application/json' \
        -d ''
    :param archive: tgz, xz, tar.gz, or tar file with workflow files
    :type archive: str
    curl -X 'POST' \
        'http://127.0.0.1:8000/upload?archive=ThePathToYourArchiveFile' \
        -H 'accept: application/json' \
        -d ''
    :param yaml: yaml file with workflow specifications
    :type yaml: str
    curl -X 'POST' \
        'http://127.0.0.1:8000/upload?yaml=~/cm/cloudmesh-cc/tests/workflow-example/workflow-example.yaml' \
        -H 'accept: application/json' \
        -d ''
    :return: success or failure message
    """
    from pathlib import Path
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
            #expanded_dir_path = Path(expanded_dir_path).as_posix()

            # these try excepts are needed in the case of a workflow with
            # all py files! or all sh files! or all ipynb files!
            try:
                Shell.run(f'cp {expanded_dir_path}*.yaml {runtime_directory}')
            except:
                pass
            try:
                Shell.run(f'cp {expanded_dir_path}*.sh {runtime_directory}')
            except:
                pass
            try:
                Shell.run(f'cp {expanded_dir_path}*.py {runtime_directory}')
            except:
                pass
            try:
                Shell.run(f'cp {expanded_dir_path}*.ipynb {runtime_directory}')
            except:
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
            from pathlib import Path
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
# url = 'http://127.0.0.1:8000/upload'
# file = {'file': open('images/1.png', 'rb')}
# resp = requests.post(url=url, files=file)
# print(resp.json())

@app.delete("/workflow/{name}", tags=['workflow'])
def delete_workflow(name: str, job: str = None):
    """
    deletes the job in the specified workflow if specified;
    if the job is not specified, then deletes entire workflow

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


@app.get("/workflow/{name}", tags=['workflow'])
def get_workflow(request: Request, name: str, job: str = None, output: str = None):
    """
    retrieves a job in a workflow, if specified. if not specified,
    retrieves an entire workflow

    you need to have first uploaded the workflow-example for this curl to work!
    curl -X 'GET' \
        'http://127.0.0.1:8000/workflow/workflow-example' \
        -H 'accept: application/json'
    :param name: name of the workflow
    :type name: str
    :param job: name of the job
    :type job: str
    :param output: how to print workflow. can be html or table
    :type output: str
    :return: success or failure message
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
            # we must initialize preferences in case they dont exist
            configuration_file = Shell.map_filename(
                '~/.cloudmesh/workflow/table-preferences.yaml').path
            if not os.path.isfile(configuration_file):
                table_preferences = {
                    'id': True,
                    'name': True,
                    'progress': True,
                    'status': True
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
            workflow_dict = Printer.dict(w.graph.nodes, order=order)
            status_dict = w.analyze_states()

            configuration_file = Shell.map_filename(
                '~/.cloudmesh/workflow/table-preferences.yaml').path
            preferences = {'id': True, 'name': True, 'progress': True,
                           'status': True}
            if os.path.isfile(configuration_file):
                preferences = yaml.safe_load(
                    Path(configuration_file).read_text())

            return templates.TemplateResponse("workflow-table.html",
                                              {"request": request,
                                               "dictionary": w.graph.nodes,
                                               "name_of_workflow": name,
                                               "workflowlist": folders,
                                               "status_dict": status_dict,
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


@app.get("/workflow-graph/{name}", tags=['portal'], include_in_schema=include_in_schema_portal_tag)
def get_workflow_graph(request: Request, name: str):
    """
    see the graph embedded within web interface
    :param request: type of request (api does this automatically in browser)
    :type request: Request
    :param name: name of workflow to retrieve the graph for
    :type name: str
    :return: html page with graph
    """
    folders = get_available_workflows()
    svg = f"http://127.0.0.1:8000/workflow/{name}?output=graph"
    import requests
    r = requests.get(svg)
    # r = '''
    # <ul>
    #     <li>
    #         hello
    #     </li>
    # </ul>
    # '''

    print(r.text)
    w = load_workflow(name)
    status_dict = w.analyze_states()
    return templates.TemplateResponse("workflow-graph.html",
                                      {"request": request,
                                       "svg": r.text,
                                       "name_of_workflow": name,
                                       "workflowlist": folders,
                                       "status_dict": status_dict})


@app.get("/run/{name}", tags=['workflow'])
def run_workflow(request: Request, name: str, run_type: str = "topo"):
    """
    runs a specified workflow according to provided run type

    example curl:
    we need to have first uploaded workflow-example for this curl to work!
    curl -X 'GET' \
        'http://127.0.0.1:8000/run/workflow-example?run_type=topo' \
        -H 'accept: application/json'
    :param name: name of workflow
    :type name: str
    :param run_type: type of run, either topo or parallel
    :type run_type: str
    :return: success or exception message
    """
    w = load_workflow(name)
    w.create_topological_order()
    os.chdir(os.path.dirname(w.filename))

    try:
        if run_type == "topo":
            threading.Thread(target=w.run_topo, kwargs={'show': True}).start()
            #w.run_topo(show=True)
        else:
            threading.Thread(target=w.run_parallel, kwargs={'show': True}).start()
            #w.run_parallel(show=True)
        #return {"Success": "Workflow ran successfully"}
        return RedirectResponse(url=f'/workflow-running/{w.name}')
    except Exception as e:
        print("Exception:", e)

@app.get("/workflow-running/{name}", tags=['portal'], include_in_schema=include_in_schema_portal_tag)
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

    from pprint import pprint

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
        #print(node_name)
        #print(w.graph.nodes.keys())
        if job_name not in original_yaml_file['workflow']['nodes']:
            del runtime_yaml_file['workflow']['nodes'][job_name]
        #else:
        #    runtime_yaml_file['workflow']['nodes'][job_name]['no'] = dict_with_order['nodes'][job_name]['no']
      #banner(str(w.graph.nodes[job_name]['progress']))
    #pprint.pprint(w.graph.nodes)

    # this is copy pasted from analyze_states from workflow.py
    # because i cant find a better way to call it
    # (initializing a workflow object would overwrite the
    # runtime yaml, thats NOT what we want!) so we're stuck with this
    states = []
    for state in ['done', 'ready', 'failed', 'submitted', 'running']:
        states.append(state)
    for job_name in runtime_yaml_file['workflow']['nodes']:
        states.append(runtime_yaml_file['workflow']['nodes'][job_name]["status"])

    from collections import Counter
    count = Counter(states)
    for state in ['done', 'ready', 'failed', 'submitted', 'running']:
        count[state] = count[state] - 1

    pprint(runtime_yaml_file['workflow']['nodes'])

    configuration_file = Shell.map_filename(
        '~/.cloudmesh/workflow/table-preferences.yaml').path
    preferences = {'id': True, 'name': True, 'progress': True,
                   'status': True}
    if os.path.isfile(configuration_file):
        preferences = yaml.safe_load(
            Path(configuration_file).read_text())

    return templates.TemplateResponse("workflow-running.html",
                                      {"request": request,
                                       "dictionary": runtime_yaml_file['workflow']['nodes'],
                                       "name_of_workflow": name,
                                       "status_dict": count,
                                       "workflowlist": folders,
                                       "preferences": preferences})

@app.get("/add-job/{name_of_workflow}", tags=['workflow'])
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
    This command adds a node to a workflow. with the specified arguments. A check
                is returned and the user is alerted if arguments are missing
                arguments are passed in ATTRIBUTE=VALUE fashion.
                if the name of the workflow is omitted, the default workflow is used.
                If no job name is specified, an automated number that is kept in the
                config.yaml file will be used and the name will be job-n

    example curl:
    we need to have first uploaded workflow-example for this curl to work!
    curl -X 'GET' \
        'http://127.0.0.1:8000/add-job/workflow-example?job=myCoolJob&user=CoolPerson&host=local&kind=local&status=ready&script=coolJob.sh&progress=0&label=CoolLabel' \
        -H 'accept: application/json'
    :param name_of_workflow: the name of the workflow
    :type name_of_workflow: str
    :param job: the specifications and characteristics of the job
    :type job: Jobpy
    :return: returns jobs within the specified workflow
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

@app.get('/preferences')
def preferences_post(request: Request):
    """
    preferences page
    :return: preferences page
    """
    folders = get_available_workflows()
    # read this from configuration file
    configuration_file = Shell.map_filename(
        '~/.cloudmesh/workflow/table-preferences.yaml').path
    preferences = {'id': False, 'name': False, 'progress': False,
                   'status': False}
    if os.path.isfile(configuration_file):
        preferences = yaml.safe_load(Path(configuration_file).read_text())
    #for key, value in preferences.items():
        #if value:
            #value = 'checked'
    #page = "cloudmesh/cc/service/markdown/contact.md"
    #import markdown
    #contact = readfile(page)
    #html = markdown.markdown(contact)
    r = templates.TemplateResponse("preferences.html",
                                      {"request": request,
                                       "workflowlist": folders,
                                       "preferences": preferences})
    from pprint import pprint
    pprint(r)
    return r

@app.post('/preferences', status_code=204, response_class=Response)
def preferences_post(request: Request, id: bool = Form(False),
                     name: bool = Form(False),
                     progress: bool = Form(False),
                     status: bool = Form(False)):
    folders = get_available_workflows()
    #print(preferences)
    table_preferences = {
        'id': id,
        'name': name,
        'progress': progress,
        'status': status
    }
    dot_cloudmesh_dir = Shell.map_filename('~/.cloudmesh/workflow').path
    configuration_file = Shell.map_filename(
        '~/.cloudmesh/workflow/table-preferences.yaml').path
    if not os.path.isdir(dot_cloudmesh_dir):
        Shell.mkdir(dot_cloudmesh_dir)
    #if not os.path.isfile(configuration_file):
    with open(configuration_file, 'w') as f:
        yaml.dump(table_preferences, f, default_flow_style=False,
                  sort_keys=False)

@app.get('/generate-example', status_code=302, response_class=RedirectResponse)
def generate_example_workflow(request: Request):
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
    # command = f'tar --strip-components 1 --force-local -xvf {tar_location} -C {runtime_directory}'
    #
    # print(command)
    # os.system(command)
    # Shell.rm(f'{tar_location}')
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


#
# QUEUES
#
# @app.get("/queues/", response_class=HTMLResponse)
# async def list_queues(request: Request):
#     global q
#     return templates.TemplateResponse('templates/queues.html',
#                                       {"request": request,
#                                        "queues": q.queues})
#
#
# #TODO: fix
# @app.post("/queue")
# async def add_queue(name: str):
#     global q
#     q.create(name=name)
#     return {
#         "queues": q.queues
#     }
#
# # TODO this may not be right
# @app.delete("/queue/{name}")
# async def delete_queue(name: str):
#     global q
#     q.remove(name)
#     return {
#         "queues": q.queues
#     }
#
#
# #
# # JOBS
# #
#
# #TODO: fix
# @app.post("/job")
# async def add_job(name: str, job: str, command: str):
#     global q
#     q.add(name=name, job=job, command=command)
#     return {
#         "jobs": q.queues[name]
#     }
#
# # TODO this may not be right
# @app.delete("/job/{queue}/{name}")
# async def delete_job(name: str, queue:str):
#     global q
#     q.remove(name)
#     return {
#         "jobs": q.queues[name]
#     }
#
# @app.get("/jobs/{queue}", response_class=HTMLResponse)
# async def list_jobs(request: Request, queue: str):
#     global q
#     jobs = []
#     for q in q.queues:
#         if q == queue:
#             for job in q.queues[queue]:
#                 jobs.append(q.queues[queue][job])
#     order = q.queues[queue][job][0:1]
#     order = [word.capitalize() for word in order]
#     Console.error(str(order))
#
#     return templates.TemplateResponse("templates/item.html",
#                                       {"request": request,
#                                        "no": no,
#                                        "jobs": jobs,
#                                        "order": order})
#
#
# @app.get("/job/{queue}/{job}", response_class=HTMLResponse)
# async def read_job(queue: str, job: str):
#     global q
#     result = Printer.attribute(q.queues[queue][job], output='html')
#     name = q.queues[queue][job]["name"]
#     d = f"<h1>{name}</h1>"
#     d += "<table>"
#     d += f"<tr> <th> attribute </th><th> value </th> </tr>"
#
#     for attribute in q.queues[queue][job]:
#         value = q.queues[queue][job][attribute]
#         d += f"<tr> <td> {attribute} </td><td> {value} </td> </tr>"
#     d += "</table>"
#     result = d
#     print(Printer.attribute(q.queues[queue][job]))
#     print(result)
#
#     page = f"""
#     <html>
#         <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.css">
#         <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.js"></script>
#         <head>
#             <title>Some HTML in here</title>
#         </head>
#         <body>
#             {result}
#         </body>
#     </html>
#     """
#     return page
