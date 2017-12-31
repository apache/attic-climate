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

'''
Classes:
    DatasetLoader - Generate OCW Dataset objects from a variety of sources.
'''

import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.data_source.podaac_datasource as podaac
import warnings

class DatasetLoader:
    '''Generate a list of OCW Dataset objects from a variety of sources.'''

    def __init__(self, *loader_opts):
        '''Generate a list of OCW Dataset objects from a variety of sources.

        Each keyword argument can be information for a dataset in dictionary
        form. For example:

        >>> loader_opt1 = {'loader_name': 'rcmed', 'name': 'cru',
                            'dataset_id': 10, 'parameter_id': 34}
        >>> loader_opt2 = {'path': './data/TRMM_v7_3B43_1980-2010.nc,
                            'variable': 'pcp'}
        >>> loader = DatasetLoader(loader_opt1, loader_opt2)


        Or more conveniently if the loader configuration is defined in a
        yaml file named config_file (see RCMES examples):

        >>> import yaml
        >>> config = yaml.load(open(config_file))
        >>> obs_loader_config = config['datasets']['reference']
        >>> loader = DatasetLoader(*obs_loader_config)


        As shown in the first example, the dictionary for each argument should
        contain a loader name and parameters specific to the particular loader.
        Once the configuration is entered, the datasets may be loaded using:

        >>> loader.load_datasets()
        >>> obs_datasets = loader.datasets


        Additionally, each dataset must have a ``loader_name`` keyword. This may
        be one of the following:

        * ``'local'`` - One or multiple dataset files in a local directory
        * ``'local_split'`` - A single dataset split accross multiple files in a
                            local directory
        * ``'esgf'``    - Download the dataset from the Earth System Grid
                        Federation
        * ``'rcmed'`` - Download the dataset from the Regional Climate Model
                        Evaluation System Database
        * ``'dap'`` - Download the dataset from an OPeNDAP URL
        * ``'podaac'``  - Download the dataset from Physical Oceanography
                        Distributed Active Archive Center


        Users who wish to load datasets from loaders not described above may
        define their own custom dataset loader function and incorporate it as
        follows:

        >>> loader.add_source_loader('my_loader_name', my_loader_func)


        :param loader_opts: Dictionaries containing the each dataset loader
                            configuration, representing the keyword arguments of
                            the loader function specified by an additional key
                            called 'loader_name'. If not specified by the user,
                            this defaults to local.
        :type loader_opts: :class:`dict`

        :raises KeyError: If an invalid argument is passed to a data source
                            loader function.
        '''
        # dataset loader config
        self.set_loader_opts(*loader_opts)

        # Default loaders
        self._source_loaders = {
            'local': local.load_multiple_files,
            'local_split': local.load_dataset_from_multiple_netcdf_files,
            'rcmed': rcmed.parameter_dataset,
            'podaac': podaac.extract_l4_granule
        }
        
        # Exclude esgf and dap for python 3 until they are compatible
        try:
            import ocw.data_source.esgf as esgf
            import ocw.data_source.dap as dap
            self._source_loaders['dap'] = dap.load
            self._source_loaders['esgf'] = esgf.load_dataset
        except ImportError:
            warnings.warn('dap and esgf loaders missing. If these are needed, '
                          'fallback to python 2.7.x.')

    def add_source_loader(self, loader_name, loader_func):
        '''
        Add a custom source loader.

        :param loader_name: The name of the data source.
        :type loader_name: :mod:`string`

        :param loader_func: Reference to a custom defined function. This should
                            return an OCW Dataset object, and have an origin which satisfies
                            origin['source'] == loader_name.
        :type loader_func: :class:`callable`
        '''
        self._source_loaders[loader_name] = loader_func

    def add_loader_opts(self, *loader_opts):
        '''
        A convenient means of adding loader options for each dataset to the
        loader.

        :param loader_opts: Dictionaries containing the each dataset loader
                            configuration, representing the keyword arguments of
                            the loader function specified by an additional key
                            called 'loader_name'. If not specified by the user,
                            this defaults to local.
        :type loader_opts: :mod:`dict`
        '''
        for opt in loader_opts:
            if 'loader_name' not in opt:
                opt['loader_name'] = 'local'
        self._config.extend(loader_opts)

    def set_loader_opts(self, *loader_opts):
        '''
        Reset the dataset loader config.

        :param loader_opts: Dictionaries containing the each dataset loader
                            configuration, representing the keyword arguments of
                            the loader function specified by an additional key
                            called 'loader_name'. If not specified by the user,
                            this defaults to local.
        :type loader_opts: :mod:`dict`
        '''
        self._config = []
        self.add_loader_opts(*loader_opts)

    def load_datasets(self):
        '''
        Loads the datasets from the given loader configurations.
        '''
        # Ensure output is clear if loading is performed more than once to
        # prevent duplicates.
        self.datasets = []

        # Load the datasets
        for loader_opt in self._config:
            output = self._load(**loader_opt)

            # Need to account for the fact that some loaders return lists
            # of OCW Dataset objects instead of just one
            if isinstance(output, list):
                self.datasets.extend(output)
            else:
                self.datasets.append(output)

    def _load(self, **kwargs):
        '''
        Generic dataset loading method.
        '''
        # Extract the loader name
        loader_name = kwargs.pop('loader_name')

        # Find the correct loader function for the given data source
        loader_func = self._source_loaders[loader_name]

        # The remaining kwargs should be specific to the loader
        output = loader_func(**kwargs)

        # Preserve loader_name info for later use
        kwargs['loader_name'] = loader_name
        return output
