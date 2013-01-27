'''
Example main program for ESGF-RCMES integration.
    
'''

# constant parameters
USER_OPENID = "https://esg-datanode.jpl.nasa.gov/esgf-idp/openid/lucacinquini"
USER_PASSWORD = "*****"
DATA_DIRECTORY = "/tmp"

from esgf.rcmes.logon import logon
from esgf.rcmes.logon2 import logon2
from esgf.rcmes.search import SearchClient
from esgf.rcmes.download import download

def main():
    '''Example driver program'''
    
    # step 1: obtain short-term certificate
    print 'Retrieving ESGF certificate...'
    # logon using client-side MyProxy libraries
    #if logon(USER_OPENID, USER_PASSWORD):
    #    print "...done."
    # logon through server-side MyProxy service
    if logon2(USER_OPENID, USER_PASSWORD):
        print "...done"
    
    # step 2: execute faceted search for files
    urls = main_obs4mips()
    #urls = main_cmip5()
    
    # step 3: download file(s)
    for i, url in enumerate(urls):
        if i>=1:
            break
        download(url, toDirectory=DATA_DIRECTORY)

    
def main_cmip5():
    '''
    Example workflow to search for CMIP5 files
    '''
    
    searchClient = SearchClient(searchServiceUrl="http://pcmdi9.llnl.gov/esg-search/search", distrib=False)
    
    print '\nAvailable projects=%s' % searchClient.getFacets('project')
    searchClient.setConstraint(project='CMIP5')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    print '\nAvailable models=%s' % searchClient.getFacets('model')
    searchClient.setConstraint(model='INM-CM4')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    print '\nAvailable experiments=%s' % searchClient.getFacets('experiment')
    searchClient.setConstraint(experiment='historical')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    print '\nAvailable time frequencies=%s' % searchClient.getFacets('time_frequency')
    searchClient.setConstraint(time_frequency='mon')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()

    print '\nAvailable CF standard names=%s' % searchClient.getFacets('cf_standard_name')
    searchClient.setConstraint(cf_standard_name='air_temperature')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    urls = searchClient.getFiles()
    return urls
    
    
def main_obs4mips():
    '''
    Example workflow to search for obs4MIPs files.
    '''
    
    searchClient = SearchClient(distrib=False)
    
    # obs4MIPs
    print '\nAvailable projects=%s' % searchClient.getFacets('project')
    searchClient.setConstraint(project='obs4MIPs')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    print '\nAvailable variables=%s' % searchClient.getFacets('variable')
    searchClient.setConstraint(variable='hus')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    print '\nAvailable time frequencies=%s' % searchClient.getFacets('time_frequency')
    searchClient.setConstraint(time_frequency='mon')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    print '\nAvailable models=%s' % searchClient.getFacets('model')
    searchClient.setConstraint(model='Obs-MLS')
    print "Number of Datasets=%d" % searchClient.getNumberOfDatasets()
    
    urls = searchClient.getFiles()
    return urls

if __name__ == '__main__':
    main()