'''This is a collection of functions that provide the single interface to the
rcmed.  Initial design will includes several functions to interact with the 
available parameters within rcmed and their metadata.

Future work includes rolling the rcmed querying code into this module as well.
'''

import requests, json

paramUri = 'http://rcmes.jpl.nasa.gov/bottle/rcmed/param.json'

def getParams(uri=paramUri):
    '''This will return all of the parameters from the database as
    a list of dictionaries.
    
    If the database is not available, then the method will return None'''
    # Use a get request to call the Web Service
    try:
        httpRequest = requests.get(uri)
    except:
        print "HTTPRequest failed.  Bottle WebServer is offline"
        raise
    # TODO Check the request status code if it is 400 or 500 range then 
    #      return None
    # if the status code is 200 then return the request.text's param list
    # http_request.status_code is an int we can inspect
    paramDict = json.loads(httpRequest.text)
    paramList = paramDict['param']
    
    filteredParams = []
    # Filter list to remove missing data values
    for param in paramList:
        paramGood = True
        for key, value in param.iteritems():
            if value == None:
                paramGood = False
        
        if paramGood:
            filteredParams.append(param)
        else:
            filteredParams.append(param)
    
    
    return filteredParams



#class Parameter(object):
#    
#    def __init__(self):
#        self.param_query_uri = 'http://some.url'
#        self.param_list = self.param_metadata()
#        
#    def param_metadata(self):
#        '''This method will return a list of python dict's.  Each dict will 
#        contain a complete record for each parameter from rcmed'''
#        # 1.  Query the Parameters Metadata Endpoint using param_query_uri
#        # 2.  Parse the returned data and re-format into a dict
#        # 3.  define self.para_met_dict
#        test_list = [{"id":12,
#                      "description":"ERA Dataset 2 Metre Temperature",
#                      "type":'temp'
#                      },
#                      {"id":13,
#                       "description":"ERA Dataset 2 Metre Dewpoint Temperature",
#                       'type':'temp'
#                       },
#                      {"id":14,
#                       "description":"TRMM Dataset HRF parameter",
#                       'type':'hrf'
#                        }
#                     ]
#        print "self.param_met_dict has been created"
#        return test_list
#    
#    def get_param_by_id(self, id):
#        '''This will take in a parameter id and return a single dict.  Can we 
#        safely assume we will always hold a unique parameter id?  - Currently
#        this is True'''
#        for p in self.param_list:
#            if p['id'] == id: 
#                return p
#            else: 
#                pass
#    
#    def get_params_by_type(self, type):
#        '''This will take in a parameter type like precip, temp, pressure, etc.
#        and will return a list of all the params that are of the given type.'''
#        param_list = [] #empty list to collect the param dicts
#        for p in self.param_list:
#            if p['type'] == type:
#                param_list.append(p)
#            else:
#                pass
#        return param_list
#
#
#class ObsData(object):
#    
#    def __init__(self):
#        self.query_url = 'http://rcmes/rcmed....'  #can we merely insert the query criteria into the url attribute?
#        self.param_id = 6
#        self.dataset_id = 1
#        self.lat_range = [25.4,55.0]
#        self.lon_range = [0.0,10.7]
#        self.time_range = [start,end]
#        
#    def set_param(self, param_dict):
#        self.param_id = param_dict['id']
#        self.dataset_id = null
#        # look up the dataset id using the parameter id and set it
#        p = Parameter.get_param_by_id(id)
        