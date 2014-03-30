Evaluation UI Webservices
*************************

The OCW evaluation UI is a demonstration web application that is built upon the
OCW toolkit. The web services for the application are written in Python on top
of the Bottle Web Framework.

Configuration and Dependencies
==============================

The Evaluation UI is built on top of the OCW toolkit and as such requires it to
function properly. Please check the toolkit's documentation for relevant
installation instructions. You will also need to ensure that you have Bottle
installed. You can install it with:

.. code::
    
    pip install bottle

The backend serves the static files for the evaluation frontend as well. If you
plan to use the frontend you need to ensure that the *app* directory is present
in the main web service directory. The easiest way to do this is to create a
symbolic link where the *run_webservices* module is located. Assuming you have
the entire *ocw-ui* directory, you can do this with the following command.

.. code::

    cd ocw-ui/backend
    ln -s ../frontend/app app

Finally, to start the backend just run the following command.

.. code::

    python run_webservices.py
    
Web Service Explanation
=======================

The backend endpoints are broken up into a number of modules for ease of
maintenance and understanding. The *run_webservices* module is the primary
application module. It brings together all the various submodules into a
useful system. It also defines a number of helpful endpoints for returning
static files such as the index page, CSS files, JavaScript files, and more.

Local File Metadata Extractors
------------------------------

The *local_file_metadata_extractors* module contains all the endpoints that are
used to strip information out of various objects for display in the UI. At the
moment, the main functionality is stripping out metadata from NetCDF files when
a user wishes to *load* a local file into the evaluation.

.. autobottle:: local_file_metadata_extractors:lfme_app

Directory Helpers
-----------------

The *directory_helpers* module contains a number of endpoints for working
directory manipulation. The frontend uses these endpoints to grab directory
information (within a prefix path for security), return result directory
information, and other things.

.. autobottle:: directory_helpers:dir_app

RCMED Helpers
-------------

The *rcmed_helpers* module contains endpoints for loading datasets from the
Regional Climate Model Evaluation Database at NASA's Jet Propulsion Laboratory.

.. autobottle:: rcmed_helpers:rcmed_app

Processing Endpoints
--------------------

The *processing* module contains all the endpoints related to the running of
evaluations.

.. autobottle:: processing:processing_app
