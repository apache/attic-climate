'''Module containing constant parameters for ESGF RCMES integration.'''

# default location of ESGF user credentials
ESGF_CREDENTIALS = "~/.esg/credentials.pem"

# URL for ESGF certificate service
#CERT_SERVICE_URL = "https://localhost:8443/esgf-idp/idp/getcert.htm"
CERT_SERVICE_URL = "https://test-datanode.jpl.nasa.gov/esgf-idp/idp/getcert.htm"

# Basic authentication realm
REALM = "ESGF"

# DN of JPL MyProxy server (needs to be explicitely set somtimes)
JPL_MYPROXY_SERVER_DN = "/O=ESGF/OU=esg-datanode.jpl.nasa.gov/CN=host/esg-vm.jpl.nasa.gov"

# URL of ESGF search service to contact
JPL_SEARCH_SERVICE_URL = "http://esg-datanode.jpl.nasa.gov/esg-search/search"
