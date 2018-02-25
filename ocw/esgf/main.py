#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
"""
Example main program for ESGF-RCMES integration.

"""

from __future__ import print_function

from ocw.esgf.download import download
from ocw.esgf.logon import logon
from ocw.esgf.search import SearchClient

# constant parameters
DATA_DIRECTORY = "/tmp"


def main():
    """Example driver program"""

    username = raw_input('Enter your ESGF Username:\n')
    password = raw_input('Enter your ESGF Password:\n')

    # step 1: obtain short-term certificate
    print('Retrieving ESGF certificate...')
    # logon using client-side MyProxy libraries
    if logon(username, password):
        print("...done.")

    # step 2: execute faceted search for files
    # urls = main_obs4mips()
    urls = main_cmip5()

    # step 3: download file(s)
    for i, url in enumerate(urls):
        if i >= 1:
            break
        download(url, toDirectory=DATA_DIRECTORY)


def main_cmip5():
    """
    Example workflow to search for CMIP5 files
    """

    search_client = SearchClient(
        searchServiceUrl="http://pcmdi9.llnl.gov/esg-search/search", distrib=False)

    print('\nAvailable projects=%s' % search_client.getFacets('project'))
    search_client.setConstraint(project='CMIP5')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable models=%s' % search_client.getFacets('model'))
    search_client.setConstraint(model='INM-CM4')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable experiments=%s' % search_client.getFacets('experiment'))
    search_client.setConstraint(experiment='historical')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable time frequencies=%s' % search_client.getFacets('time_frequency'))
    search_client.setConstraint(time_frequency='mon')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable CF standard names=%s' % search_client.getFacets('cf_standard_name'))
    search_client.setConstraint(cf_standard_name='air_temperature')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    urls = search_client.getFiles()

    return urls


def main_obs4mips():
    """
    Example workflow to search for obs4MIPs files.
    """

    search_client = SearchClient(distrib=False)

    # obs4MIPs
    print('\nAvailable projects=%s' % search_client.getFacets('project'))
    search_client.setConstraint(project='obs4MIPs')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable variables=%s' % search_client.getFacets('variable'))
    search_client.setConstraint(variable='hus')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable time frequencies=%s' % search_client.getFacets('time_frequency'))
    search_client.setConstraint(time_frequency='mon')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    print('\nAvailable models=%s' % search_client.getFacets('model'))
    search_client.setConstraint(model='Obs-MLS')
    print("Number of Datasets=%d" % search_client.getNumberOfDatasets())

    urls = search_client.getFiles()

    return urls


if __name__ == '__main__':
    main()
