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


import ocw.utils as utils
import numpy as np
from scipy.stats import percentileofscore, linregress

class Downscaling:
    def __init__(self, ref_dataset, model_present, model_future):
        '''
        :param ref_dataset: The Dataset to use as the reference dataset (observation)
        :type ref_dataset: Dataset
        :param model_present: model simulation to be compared with observation
        :type model_present: Dataset
        :param model_future: model simulation to be calibrated for prediction
        :type model_future: Dataset
        '''
        self.ref_dataset = ref_dataset[~ref_dataset.mask].ravel()
        self.model_present = model_present.ravel()
        self.model_future = model_future.ravel()
             
    description = "statistical downscaling methods"

    def Delta_addition(self):
        '''Calculate the mean difference between future and present simulation, 
           then add the difference to the observed distribution

        :returns: downscaled model_present and model_future
        ''' 
        ref = self.ref_dataset 
        model_present = self.model_present 
        model_future = self.model_future 

        return model_present, ref + np.mean(model_future-model_present)

    def Delta_correction(self):
        '''Calculate the mean difference between observation and present simulation,
           then add the difference to the future distribution

        :returns: downscaled model_present and model_future
        '''
        ref = self.ref_dataset
        model_present = self.model_present
        model_future = self.model_future

        return model_present+np.mean(ref) - np.mean(model_present), model_future + np.mean(ref) - np.mean(model_present)

    def Quantile_mapping(self):
        '''Remove the biases for each quantile value 
        Wood et al (2004) HYDROLOGIC IMPLICATIONS OF DYNAMICAL AND STATISTICAL APPROACHES TO DOWNSCALING CLIMATE MODEL OUTPUTS

        :returns: downscaled model_present and model_future
        '''
        ref = self.ref_dataset
        model_present = self.model_present
        model_present_corrected = np.zeros(model_present.size)
        model_future = self.model_future
        model_future_corrected = np.zeros(model_future.size)


        for ival, model_value in enumerate(model_present):
            percentile = percentileofscore(model_present, model_value)
            model_present_corrected[ival] = np.percentile(ref, percentile) 

        for ival, model_value in enumerate(model_future):
            percentile = percentileofscore(model_future, model_value)
            model_future_corrected[ival] = model_value + np.percentile(ref, percentile) - np.percentile(model_present, percentile) 

        return model_present_corrected, model_future_corrected     

    def Asynchronous_regression(self):
        '''Remove the biases by fitting a linear regression model with ordered observational and model datasets
        Stoner et al (2013) An asynchronous regional regression model for statistical downscaling of daily climate variables    

        :returns: downscaled model_present and model_future
        '''

        ref_original = self.ref_dataset
        model_present = self.model_present
        model_present_sorted = np.sort(model_present)
        model_future = self.model_future
 
        ref = np.zeros(model_present.size)   # For linear regression, the size of reference data must be same as model data. 

        for ival, model_value in enumerate(model_present_sorted):
            percentile = percentileofscore(model_present_sorted, model_value)
            ref[ival] = np.percentile(ref_original, percentile)       

        slope, intercept = linregress(model_present_sorted, ref)[0:2] 
        
        return model_present*slope+intercept, model_future*slope+intercept





