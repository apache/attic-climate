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
"""Module containing constant parameters for ESGF RCMES integration."""

# default location of ESGF user credentials
ESGF_CREDENTIALS = "~/.esg/credentials.pem"

JPL_HOSTNAME = "esgf-node.jpl.nasa.gov"

# DN of JPL MyProxy server (needs to be explicitely set somtimes)
JPL_MYPROXY_SERVER_DN = "/O=ESGF/OU=ESGF.ORG/CN=esgf-node.jpl.nasa.gov"

# URL of ESGF search service to contact
JPL_SEARCH_SERVICE_URL = "http://esgf-node.jpl.nasa.gov/esg-search/search"
DEFAULT_ESGF_SEARCH = "http://esgf-node.jpl.nasa.gov/esg-search/search"
