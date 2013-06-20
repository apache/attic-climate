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
RCMES module to logon onto the ESGF by contacting the IdP RESTful service.
'''

from esgf.rcmes.constants import ESGF_CREDENTIALS, CERT_SERVICE_URL, REALM

import urllib2
from os.path import expanduser

def logon2(openid, password):
    '''
    Function to retrieve a short-term X.509 certificate that can be used to authenticate with ESGF.
    The certificate is written in the location specified by ESGF_CREDENTIALS.
    '''
    
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(REALM, CERT_SERVICE_URL, openid, password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    opener = urllib2.build_opener(urllib2.HTTPHandler, handler)
    request = opener.open(CERT_SERVICE_URL)
    #print request.read()
    
    localFilePath = expanduser(ESGF_CREDENTIALS)
    certFile=open(localFilePath, 'w')
    certFile.write(request.read())