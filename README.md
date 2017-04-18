## Apache Open Climate Workbench
[![Build Status](https://travis-ci.org/apache/climate.svg?branch=master)](https://travis-ci.org/apache/climate)
[![Coverage Status](https://coveralls.io/repos/github/apache/climate/badge.svg?branch=master)](https://coveralls.io/github/apache/climate?branch=master)
[![Requirements Status](https://requires.io/github/apache/climate/requirements.svg?branch=master)](https://requires.io/github/apache/climate/requirements/?branch=master)
[![Code Health](https://landscape.io/github/apache/climate/master/landscape.svg?style=flat-square)](https://landscape.io/github/apache/climate/master)
[![PyPI](https://img.shields.io/pypi/v/ocw.svg?maxAge=2592000?style=plastic)](https://pypi.python.org/pypi/ocw)
[![Python Badge](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![Anaconda-Server Badge](https://anaconda.org/agoodman/ocw/badges/installer/conda.svg)](https://anaconda.org/agoodman/ocw)

<img src="./docs/source/ocw-logo-variant-sm-01-01-new.png" width="200" />

[Apache Open Climate Workbench](http://climate.apache.org) is an effort to develop software that performs climate model evaluations using model outputs from a variety of different sources (the Earth System Grid Federation, the Coordinated Regional Downscaling Experiment, the U.S. National Climate Assessment and the North American Regional Climate Change Assessment Program) and temporal/spatial scales with remote sensing data from NASA, NOAA and other agencies. The toolkit includes capabilities for rebinning, metrics computation and visualization. For additional project information, please check the [project website](http://climate.apache.org/).

## Getting Started

The [project's wiki](https://cwiki.apache.org/confluence/display/CLIMATE/Home) is the best location for help and project information. New users should check out the [Getting Started](https://cwiki.apache.org/confluence/display/CLIMATE/Getting+Started) and [Easy OCW](https://cwiki.apache.org/confluence/display/CLIMATE/Easy-OCW+-+A+Guide+to+Simplifying+OCW+Installation) pages for help getting the necessary dependencies installed. If you would prefer to have an isolated environment set up in a virtual machine you should read the [OCW VM](https://cwiki.apache.org/confluence/display/CLIMATE/OCW+VM+-+A+Self+Contained+OCW+Environment) documentation. It will help you get up and running quickly with a fresh VM image for OCW work.

There are a number of examples in the *examples* directory to help users get started with the toolkit API. If you have questions, the best way to get help is to email the project mailing lists which can be found on the [project's community page](http://climate.apache.org/community/mailing-lists.html).

## Development

OCW always welcomes pull request. Please check the [Developer Area](https://cwiki.apache.org/confluence/display/CLIMATE/Developer+Area) on the wiki for additional information on how to contribute. The [project's JIRA](https://issues.apache.org/jira/browse/CLIMATE) is a great place to start looking for issues to solve. Make sure to stop by the mailing lists and introduce yourself as well!

## Documentation

The project host the documentation built from the last release artifact on [the project website](https://climate.apache.org/api/index.html)

If you would like to build the documentation for the project run the following command from the root of the repository:

```
cd docs && make html
```

You will need to have installed the project dependencies first. Checkout the [Getting Started](https://cwiki.apache.org/confluence/display/CLIMATE/Getting+Started) and [Easy OCW](https://cwiki.apache.org/confluence/display/CLIMATE/Easy-OCW+-+A+Guide+to+Simplifying+OCW+Installation) pages for help getting the necessary dependencies installed.


