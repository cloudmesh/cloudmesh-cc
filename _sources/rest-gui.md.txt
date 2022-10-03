# REST GUI Web Browser Interface

The web server provides a more customizable, easy-to-use interface
for the Workflow class. To start the web server, issue commands:

```bash
cd ~/cm/cloudmesh-cc
cms cc start
```

Then, in a web browser, open the link http://127.0.0.1:8000/

The browser provides an interface to view preexisting workflows
in both a DataTable format and as a graph format. Both views will
update automatically, in a live fashion, as the workflows are run,
reporting live job status and progress.

For a quick and easy example of leveraging this GUI interface,
click on the Example tab in the left-hand sidebar. Then, a
workflow-example will appear underneath Workflows. Click on the
workflow-example and run the workflow by clicking the green Run
button in the top-right. As the workflow runs, the user is able
to click on the Graph button and back to the Table button, as
desired, to view the workflow's progression.
