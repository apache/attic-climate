import requests, json

class RCMED(object):
    
    def __init__(self):
        self.param_uri = 'http://argo.jpl.nasa.gov:8886/rcmed/param.json'
        self.params = self.get_params()
    
    
    def get_params(self):
        '''This will return all of the parameters from the database as
        a list of dictionaries.
        
        If the database is not available, then the method will return None'''
        # Use a get request to call the Web Service
        try:
            http_request = requests.get(self.param_uri)
        except:
            print "HTTPRequest failed.  Bottle WebServer is offline"
            raise
        # TODO Check the request status code if it is 400 or 500 range then 
        #      return None
        # if the status code is 200 then return the request.text's param list
        # http_request.status_code is an int we can inspect
        param_dict = json.loads(http_request.text)
        param_list = param_dict['param']
        
        filtered_params = []
        # Filter list to remove missing data values
        for param in param_list:
            param_good = True
            for key, value in param.iteritems():
                if value == None:
                    param_good = False
            
            if param_good:
                filtered_params.append(param)
        
        
        return filtered_params


class RCMET(object):
    
    def __init__(self):
        self.none = None
    

        