'''
RCMES module to download a file from ESGF.

'''

import urllib2, httplib
from os.path import expanduser, join

from esgf.rcmes.constants import ESGF_CREDENTIALS

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    '''
    HTTP handler that transmits an X509 certificate as part of the request
    '''
    
    def __init__(self, key, cert):
            urllib2.HTTPSHandler.__init__(self)
            self.key = key
            self.cert = cert
    def https_open(self, req):
            return self.do_open(self.getConnection, req)
    def getConnection(self, host, timeout=300):
            return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

def download(url, toDirectory="/tmp"):
    '''
    Function to download a single file from ESGF.
    
    :param url: the URL of the file to download
    :param toDirectory: target directory where the file will be written
    '''
    
    # setup HTTP handler
    certFile = expanduser(ESGF_CREDENTIALS)
    opener = urllib2.build_opener(HTTPSClientAuthHandler(certFile,certFile))
    opener.add_handler(urllib2.HTTPCookieProcessor())
    
    # download file
    localFilePath = join(toDirectory,url.split('/')[-1])
    print "\nDownloading url: %s to local path: %s ..." % (url, localFilePath)
    localFile=open( localFilePath, 'w')
    webFile=opener.open(url)
    localFile.write(webFile.read())
    
    # cleanup
    localFile.close()
    webFile.close()
    opener.close()
    print "... done"
