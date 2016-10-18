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
'''
Example main program for ESGF-RCMES integration.
    
'''

# constant parameters
DATA_DIRECTORY = "/tmp"

from ocw.esgf.logon import logon
from ocw.esgf.search import SearchClient
from ocw.esgf.download import download


def main():
    '''Example driver program'''

    username = raw_input('Enter your ESGF Username:\n')
    password = raw_input('Enter your ESGF Password:\n')

    # step 1: obtain short-term certificate
    print('Retrieving ESGF certificate...')
    # logon using client-side MyProxy libraries
    if logon(username, password):
        print("...done.")

    # step 2: execute faceted search for files
    urls = main_obs4mips()
    #urls = main_cmip5()

    # step 3: download file(s)
    for i, url in enumerate(urls):
        if i >= 1:
            break
        download(url, toDirectory=DATA_DIRECTORY)


def main_cmip5():
    '''
    Example workflow to search for CMIP5 files
    '''

    searchClient = SearchClient(
        searchServiceUrl="http://pcmdi9.llnl.gov/esg-search/search", distrib=False)

    print('\nAvailable projects=%s' % searchClient.getFacets('project'))
    searchClient.setConstraint(project='CMIP5')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable models=%s' % searchClient.getFacets('model'))
    searchClient.setConstraint(model='INM-CM4')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable experiments=%s' % searchClient.getFacets('experiment'))
    searchClient.setConstraint(experiment='historical')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable time frequencies=%s' %
          searchClient.getFacets('time_frequency'))
    searchClient.setConstraint(time_frequency='mon')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable CF standard names=%s' %
          searchClient.getFacets('cf_standard_name'))
    searchClient.setConstraint(cf_standard_name='air_temperature')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    urls = searchClient.getFiles()
    return urls


def main_obs4mips():
    '''
    Example workflow to search for obs4MIPs files.
    '''

    searchClient = SearchClient(distrib=False)

    # obs4MIPs
    print('\nAvailable projects=%s' % searchClient.getFacets('project'))
    searchClient.setConstraint(project='obs4MIPs')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable variables=%s' % searchClient.getFacets('variable'))
    searchClient.setConstraint(variable='hus')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable time frequencies=%s' %
          searchClient.getFacets('time_frequency'))
    searchClient.setConstraint(time_frequency='mon')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasets())

    print('\nAvailable models=%s' % searchClient.getFacets('model'))
    searchClient.setConstraint(model='Obs-MLS')
    print("Number of Datasets=%d" % searchClient.getNumberOfDatasetsi())

    urls = searchClient.getFiles()
    return urls

if __name__ == '__main__':
    main()
