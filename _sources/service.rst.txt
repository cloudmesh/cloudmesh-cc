Service
=======

A convenient Web service is included in Cloudmesh cc. It allows the user to manage and
visualize the status of workflows through a Web browser interface. At this time the focus is that
the interface can be run by a singleuser on the local machine.
This allows that remote executions of workflow nodes run completely independent
from cloudmesh cc and interaction is possible in asynchronous mode.


Management
----------


To start the service use the command::

    cms cc start

For debugging purposes with outoreload on code changes, you can use the command::

    cms cc start --reload


To stop the service use the command::

    cms cc stop

To view the interface to the service use the command::

    cms cc view


Example Workflow
----------------

An example workflow can be generated while clickon on the Example sidebar menu.

Table View
----------

The workflow can then be viewed while clicking on the workflow
name listed in the sidebar under workflows. Other workflows can be uploaded and multiple
workflows can be managed. Management buttons for the workflow are included in this view.


.. figure:: images/service-table.png
   :alt: Workflow table view

   Cloudmesh cc workflow Table view


Graph View
----------

One can switch back and forth between a graph and a table view while using the
included buttons, it will take a moment to update them.


.. figure:: images/service-graph.png
   :alt: Browser API GUI for Cloudmesh Compute Cluster

   Cloudmesh cc workflow graph view
