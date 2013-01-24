'''
RCMES module to logon onto the ESGF.
'''

from pyesgf.logon import LogonManager
import os

from esgf.rcmes.constants import JPL_MYPROXY_SERVER_DN

def logon(openid, password):
    '''
    Function to retrieve a short-term X.509 certificate that can be used to authenticate with ESGF.
    The certificate is written in the location ~/.esg/credentials.pem.
    The trusted CA certificates are written in the directory ~/.esg/certificates.
    '''
    
    # Must configure the DN of the JPL MyProxy server if using a JPL openid
    if "esg-datanode.jpl.nasa.gov" in openid:  
        os.environ['MYPROXY_SERVER_DN'] = JPL_MYPROXY_SERVER_DN
        
    lm = LogonManager()
    lm.logon_with_openid(openid,password)
    return lm.is_logged_on()
    
    
    
