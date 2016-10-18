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

from pkg_resources import VersionConflict, DistributionNotFound, \
    require
from ocw.tests.test_local import create_netcdf_object
from ocw.data_source import local
from ocw import dataset_processor as dsp
import os

PIP_DEPENDENCIES_FILE = 'easy-ocw/ocw-pip-dependencies.txt'
CONDA_DEPENDENCIES_FILE = 'easy-ocw/ocw-conda-dependencies.txt'
SUCCESS_MARK = '\033[92m' + u'\u2713' + '\033[0m'
FAILURE_MARK = '\033[91m' + u'\u274C' + '\033[0m'


def fail(prefix):
    print(prefix + " " + FAILURE_MARK)


def success(prefix):
    print(prefix + " " + SUCCESS_MARK)


def check_dependencies(file):
    ''' Verify all necessary dependencies are installed '''
    for dep in file:
        dep = dep.replace('\n', '')
        # skip all comments and blank lines in dependency file
        if '#' in dep or not dep:
            continue
        try:
            require(dep)
            success(dep)
        except DistributionNotFound as df:
            fail(dep)
            dep = str(df).split(' ')[1][1:-1]
            print('\n' + dep + ' dependency missing.')
            print('Please install it using "pip/conda install ' + dep + '"')
            fail("\nDependencies")
            end()
        except VersionConflict as vc:
            fail(dep)
            print("\nRequired version and installed version differ for the "
                  "following package:\n"
                  "Required version: " + dep)
            dep_name = str(vc).split(' ')[0][1:]  # First element is '('
            dep_version = str(vc).split(' ')[1]
            print("Installed version: " + dep_name + "==" + dep_version)
            fail("\nDependencies")
            end()


def check_dataset_loading():
    ''' Try loading test dataset '''
    dataset = None
    try:
        file_path = create_netcdf_object()
        dataset = local.load_file(file_path, variable_name='value')
    except Exception as e:
        fail("\nDataset loading")
        print("The following error occured")
        print(e)
        end(dataset)
    success("\nDataset loading")
    return dataset


def check_some_dataset_functions(dataset):
    ''' Run a subset of dataset functions and check for any exception '''
    try:
        dataset.spatial_boundaries()
        dataset.temporal_boundaries()
        dataset.spatial_resolution()
    except Exception as e:
        fail("\nDataset functions")
        print("Following error occured:")
        print(str(e))
        end(dataset)
    success("\nDataset functions")


def check_some_dsp_functions(dataset):
    '''
    Run a subset of dataset processor functions and check for
    any kind of exception.
    '''
    try:
        dsp.temporal_rebin(dataset, 'annual')
        dsp.ensemble([dataset])
    except Exception as e:
        fail("\nDataset processor functions")
        print("Following error occured:")
        print(str(e))
        end()
    finally:
        os.remove(dataset.origin['path'])
    success("\nDataset processor functions")


def end(dataset=None):
    ''' Exit program with status 1 '''
    if dataset:
        os.remove(dataset.origin['path'])
    'End program execution with return code 1'
    print('\033[91m' + "Some checks were unsuccessful")
    print("Please Fix them and run the test again." + '\033[0m')
    exit(1)


def main():
    pip_file = open(PIP_DEPENDENCIES_FILE, 'r')
    conda_file = open(CONDA_DEPENDENCIES_FILE, 'r')
    print("Checking installed dependencies\n")
    check_dependencies(conda_file)
    check_dependencies(pip_file)
    success("\nDependencies")
    dataset = check_dataset_loading()
    check_some_dataset_functions(dataset)
    check_some_dsp_functions(dataset)
    success("\nAll checks successfully completed")
    return 0

if __name__ == '__main__':
    main()
