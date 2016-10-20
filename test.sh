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

set -e  # causes the shell to exit if any subcommand or pipeline returns a non-zero status.
echo ""
echo "---------------- Running Smoke Tests ---------------"
python test_smoke.py
echo "---------------- Smoke Tests Successfully Completed---------------"
echo ""

# nosetests config file should be in home directory
cp .noserc $HOME/.noserc

# Exclude dap tests if using python 3
if [[ "$1" != "2.7" ]]; then
  export NOSE_EXCLUDE_TESTS=ocw.tests.test_dap.TestDap
fi

echo "---------------- Running Unit Tests ---------------"
nosetests
echo "---------------- All Tests successfully completed ---------------"
