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

import os
import unittest
from webtest import TestApp

from ..run_webservices import app

test_app = TestApp(app)

class TestInitialization(unittest.TestCase):
    def test_status_page(self):
        response = test_app.get('/')

        self.assertEqual(response.status_int, 200)

class TestStaticEvalResults(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists('/tmp/ocw'): os.mkdir('/tmp/ocw')
        if not os.path.exists('/tmp/ocw/foo.txt'): 
            open('/tmp/ocw/foo.txt', 'a').close()

    @classmethod
    def tearDownClass(self):
        os.remove('/tmp/ocw/foo.txt')
        os.rmdir('/tmp/ocw')

    def test_static_eval_results_return(self):
        response = test_app.get('/static/eval_results//foo.txt')

        self.assertEqual(response.status_int, 200)
if __name__ == '__main__':
    unittest.main()
