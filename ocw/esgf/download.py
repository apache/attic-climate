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
"""
OCW module to download a file from ESGF.

"""

from __future__ import print_function

import sys
from os.path import expanduser, join

from ocw.esgf.constants import ESGF_CREDENTIALS

if sys.version_info[0] >= 3:
    from http.client import HTTPSConnection
    from urllib.request import build_opener
    from urllib.request import HTTPCookieProcessor
    from urllib.request import HTTPSHandler
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from httplib import HTTPSConnection
    from urllib2 import build_opener
    from urllib2 import HTTPCookieProcessor
    from urllib2 import HTTPSHandler


class HTTPSClientAuthHandler(HTTPSHandler):
    """
    HTTP handler that transmits an X509 certificate as part of the request
    """

    def __init__(self, key, cert):
        HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        """
        Opens the https connection.
        :param req:  The https request object.
        :return: An addinfourl object for the request.
        """
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        """
        Create an HTTPSConnection object.
        :param host: The ESGF server to connect to.
        :param timeout: Connection timeout in seconds.
        :return:
        """
        return HTTPSConnection(host, key_file=self.key, cert_file=self.cert, timeout=timeout)


def download(url, toDirectory="/tmp"):
    """
    Function to download a single file from ESGF.
    :param url: the URL of the file to download
    :param toDirectory: target directory where the file will be written
    """

    # setup HTTP handler
    cert_file = expanduser(ESGF_CREDENTIALS)
    opener = build_opener(HTTPSClientAuthHandler(cert_file, cert_file))
    opener.add_handler(HTTPCookieProcessor())

    # download file
    local_file_path = join(toDirectory, url.split('/')[-1])
    print("\nDownloading url: %s to local path: %s ..." % (url, local_file_path))
    local_file = open(local_file_path, 'w')
    web_file = opener.open(url)
    local_file.write(web_file.read())

    # cleanup
    local_file.close()
    web_file.close()
    opener.close()
    print("... done")
