'''
RCMES module to execute a faceted search for ESGF files.

'''

from pyesgf.search import SearchConnection

JPL_SEARCH_SERVICE_URL = "http://esg-datanode.jpl.nasa.gov/esg-search/search"

class SearchClient():
    """
    Simple ESGF search client for RCMES.
    This class is a thin layer on top of the esgfpy-client package.
    Note: this class always searches for latest versions, no replicas.
    """
    
    def __init__(self, searchServiceUrl=JPL_SEARCH_SERVICE_URL, distrib=True):
        """
        :param searchServiceUrl: URL of ESGF search service to query
        :param distrib: True to execute a federation-wide search, 
                        False to search only the specified search service
        """
        connection = SearchConnection(searchServiceUrl, distrib=distrib)
        
        # dictionary of query constraints
        self.constraints = { "latest":True, "replica":False, "distrib":distrib } 
    
        # initial search context
        self.context = connection.new_context( **self.constraints )
        
        
    def setConstraint(self, **constraints):
        """
        Sets one or more facet constraints.
        :param constraints: dictionary of (facet name, facet value) constraints.
        """
        for key in constraints:
            print 'Setting constraint: %s=%s' % (key, constraints[key])
            self.constraints[key] = constraints[key]
        self.context = self.context.constrain(**constraints)
        
    def getNumberOfDatasets(self):
        """
        :return: the number of datasets matching the current constraints.
        """
        return self.context.hit_count
        
    def getFacets(self, facet):
        """
        :return: a dictionary of (facet value, facet count) for the specified facet and current constraints.
        Example (for facet='project'): {u'COUND': 4, u'CMIP5': 2657, u'obs4MIPs': 7} 
        """
        return self.context.facet_counts[facet]
    
    def getFiles(self):
        """
        Executes a search for files with the current constraints.
        :return: list of file download URLs.
        """
        datasets = self.context.search()
        urls = []
        for dataset in datasets:
            print "\nSearching files for dataset=%s with constraints: %s" % (dataset.dataset_id, self.constraints)
            files = dataset.file_context().search(**self.constraints)
            for file in files:
                print 'Found file=%s' % file.download_url
                urls.append(file.download_url)
        return urls
        
    
    
