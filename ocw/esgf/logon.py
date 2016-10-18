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
RCMES module to logon onto the ESGF.
'''
import os

from pyesgf.logon import LogonManager

from ocw.esgf.constants import JPL_MYPROXY_SERVER_DN, JPL_HOSTNAME


def logon(openid, password):
    '''
    Function to retrieve a short-term X.509 certificate that can be used to authenticate with ESGF.
    The certificate is written in the location ~/.esg/credentials.pem.
    The trusted CA certificates are written in the directory ~/.esg/certificates.
    '''
    # Must configure the DN of the JPL MyProxy server if using a JPL openid
    if JPL_HOSTNAME in openid:
        os.environ['MYPROXY_SERVER_DN'] = JPL_MYPROXY_SERVER_DN

    lm = LogonManager()

    lm.logon_with_openid(openid, password, bootstrap=True)

    return lm.is_logged_on()
