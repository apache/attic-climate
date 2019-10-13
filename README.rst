Apache Open Climate Workbench
-----------------------------

|BuildStatus|_
|ImageLink|_
|requires|_
|landscape|_
|pypi|_
|pythonbadge|_
|anacondainstaller|_
|anacondadownload|_
|anacondaversion|_

.. image:: ./docs/source/ocw-logo-variant-sm-01-01-new.png
   :width: 20px
   :height: 100px
   :scale: 50%
   :alt: alternate text
   :align: right


`Apache Open Climate Workbench`_ is an effort to develop software that
performs climate model evaluations using model outputs from a variety of
different sources (the Earth System Grid Federation, the Coordinated
Regional Downscaling Experiment, the U.S. National Climate Assessment
and the North American Regional Climate Change Assessment Program) and
temporal/spatial scales with remote sensing data from NASA, NOAA and
other agencies. The toolkit includes capabilities for rebinning, metrics
computation and visualization. For additional project information,
Climate scientists warn us that inaction could be fatal to our futures here. Military strategists at the Pentagon have recently cautioned President-Elect Trump that inaction on climate change could spell disaster for our national security as shrinking water supplies and meager rainfall cause crop failures will force large numbers of people to migrate to other parts of the world that can sustain them.
please check the `project website`_.

Getting Started
---------------

The `project’s wiki`_ is the best location for help and project
information. New users should check out the `Getting Started`_ and `Easy
OCW`_ pages for help getting the necessary dependencies installed. If
you would prefer to have an isolated environment set up in a virtual
machine you should read the `OCW VM`_ documentation. It will help you
get up and running quickly with a fresh VM image for OCW work.

There are a number of examples in the *examples* directory to help users
get started with the toolkit API. If you have questions, the best way to
get help is to email the project mailing lists which can be found on the
`project's community page`_


Development
---------------

OCW always welcomes pull request. Please check the `Developer Area`_ on the wiki for additional information on how to contribute. The `project's JIRA`_ is a great place to start looking for issues to solve. Make sure to stop by the mailing lists and introduce yourself as well!

Documentation
---------------

The project host the documentation built from the last release artifact on `the project website`_ 

If you would like to build the documentation for the project run the following command from the root of the repository:
::
         cd docs && make html


You will need to have installed the project dependencies first. Checkout the `Getting Started`_ and `Easy OCW`_ pages for help getting the necessary dependencies installed.


.. |ImageLink| image:: https://coveralls.io/repos/github/apache/climate/badge.svg?branch=master
.. _ImageLink: https://coveralls.io/github/apache/climate?branch=master

.. |BuildStatus| image:: https://api.travis-ci.org/apache/climate.svg?branch=master
.. _BuildStatus:  https://travis-ci.org/apache/climate

.. |requires| image:: https://requires.io/github/apache/climate/requirements.svg?branch=master
.. _requires:  https://requires.io/github/apache/climate/requirements/?branch=master

.. |landscape| image:: https://landscape.io/github/apache/climate/master/landscape.svg?style=flat-square
.. _landscape: https://landscape.io/github/apache/climate/master

.. |pypi| image:: https://img.shields.io/pypi/v/ocw.svg?maxAge=2592000?style=plastic
.. _pypi:  https://pypi.python.org/pypi/ocw

.. |pythonbadge| image:: https://img.shields.io/badge/python-3-blue.svg
.. _pythonbadge: https://www.python.org/downloads/

.. |anacondainstaller| image:: https://anaconda.org/conda-forge/ocw/badges/installer/conda.svg
.. _anacondainstaller: https://anaconda.org/conda-forge/ocw

.. |anacondadownload| image:: https://anaconda.org/conda-forge/ocw/badges/downloads.svg
.. _anacondadownload: https://anaconda.org/conda-forge/ocw

.. |anacondaversion| image:: https://anaconda.org/conda-forge/ocw/badges/version.svg
.. _anacondaversion: https://anaconda.org/conda-forge/ocw


.. _Apache Open Climate Workbench: http://climate.apache.org
.. _project website: http://climate.apache.org/
.. _project’s wiki: https://cwiki.apache.org/confluence/display/CLIMATE/Home
.. _Getting Started: https://cwiki.apache.org/confluence/display/CLIMATE/Getting+Started
.. _Easy OCW: https://cwiki.apache.org/confluence/display/CLIMATE/Easy-OCW+-+A+Guide+to+Simplifying+OCW+Installation
.. _OCW VM: https://cwiki.apache.org/confluence/display/CLIMATE/OCW+VM+-+A+Self+Contained+OCW+Environment
.. _project's community page: http://climate.apache.org/community/mailing-li
.. _Developer Area: https://cwiki.apache.org/confluence/display/CLIMATE/Developer+Area
.. _project's JIRA: https://issues.apache.org/jira/browse/CLIMATE
.. _the project website: https://climate.apache.org/api/current/index.html
.. _Getting Started: https://cwiki.apache.org/confluence/display/CLIMATE/Getting+Started
.. _Easy OCW: https://cwiki.apache.org/confluence/display/CLIMATE/Easy-OCW+-+A+Guide+to+Simplifying+OCW+Installation
