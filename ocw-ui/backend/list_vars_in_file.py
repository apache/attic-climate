#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import sys
import netCDF4
import bottle
from bottle import request
import json


@bottle.route('/list/vars/:filename#".*"#')
def list_vars(filename):
    success = 0
    filename = filename.strip('"')
    print filename + ' is filename variable'
    try:
      f = netCDF4.Dataset(filename, mode='r')
      success = 1
    except:
      print 'Error_reading_file '+filename
    
    if success:  #make some json
      var_name_list = json.dumps({'variables': f.variables.keys()}, 
                                  sort_keys=True, indent=2)
      if (request.query.callback):
          return "%s(%s)" % (request.query.callback, var_name_list)
      return var_name_list
  
    else:
      failRet = "{\"FAIL\": \""+filename+"\"}"
      if (request.query.callback):
          return "%s(%s)" % (request.query.callback, failRet)
      return failRet
