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

#Apache OCW lib immports
import ocw.data_source.local as local
import ocw.plotter as plotter
import ocw.utils as utils
from ocw.evaluation import Evaluation
import ocw.metrics as metrics

# Python libraries
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap 
from matplotlib import rcParams
from matplotlib.patches import Polygon
import string

def Map_plot_bias_of_multiyear_climatology(obs_dataset, obs_name, model_datasets, model_names,
                                      file_name, row, column, map_projection=None):
    '''Draw maps of observed multi-year climatology and biases of models"'''

    # calculate climatology of observation data
    obs_clim = utils.calc_temporal_mean(obs_dataset)
    # determine the metrics
    map_of_bias = metrics.TemporalMeanBias()

    # create the Evaluation object
    bias_evaluation = Evaluation(obs_dataset, # Reference dataset for the evaluation
                                 model_datasets, # list of target datasets for the evaluation
                                 [map_of_bias, map_of_bias])

    # run the evaluation (bias calculation)
    bias_evaluation.run() 

    rcm_bias = bias_evaluation.results[0]

    fig = plt.figure()

    lat_min = obs_dataset.lats.min()
    lat_max = obs_dataset.lats.max()
    lon_min = obs_dataset.lons.min()
    lon_max = obs_dataset.lons.max()

    string_list = list(string.ascii_lowercase) 
    ax = fig.add_subplot(row,column,1)
    if map_projection == 'npstere':
        m = Basemap(ax=ax, projection ='npstere', boundinglat=lat_min, lon_0=0,
            resolution = 'l', fix_aspect=False)
    else:
        m = Basemap(ax=ax, projection ='cyl', llcrnrlat = lat_min, urcrnrlat = lat_max,
            llcrnrlon = lon_min, urcrnrlon = lon_max, resolution = 'l', fix_aspect=False)
    lons, lats = np.meshgrid(obs_dataset.lons, obs_dataset.lats)

    x,y = m(lons, lats)

    m.drawcoastlines(linewidth=1)
    m.drawcountries(linewidth=1)
    m.drawstates(linewidth=0.5, color='w')
    max = m.contourf(x,y,obs_clim,levels = plotter._nice_intervals(obs_dataset.values, 10), extend='both',cmap='rainbow')
    ax.annotate('(a) \n' + obs_name,xy=(lon_min, lat_min))
    cax = fig.add_axes([0.02, 1.-float(1./row), 0.01, 1./row*0.6])
    plt.colorbar(max, cax = cax) 
    clevs = plotter._nice_intervals(rcm_bias, 11)
    for imodel in np.arange(len(model_datasets)):
        ax = fig.add_subplot(row, column,2+imodel)
        if map_projection == 'npstere':
            m = Basemap(ax=ax, projection ='npstere', boundinglat=lat_min, lon_0=0,
                resolution = 'l', fix_aspect=False)
        else:
            m = Basemap(ax=ax, projection ='cyl', llcrnrlat = lat_min, urcrnrlat = lat_max,
                llcrnrlon = lon_min, urcrnrlon = lon_max, resolution = 'l', fix_aspect=False)
        m.drawcoastlines(linewidth=1)
        m.drawcountries(linewidth=1)
        m.drawstates(linewidth=0.5, color='w')
        max = m.contourf(x,y,rcm_bias[imodel,:],levels = clevs, extend='both', cmap='RdBu_r')
        ax.annotate('('+string_list[imodel+1]+')  \n '+model_names[imodel],xy=(lon_min, lat_min))

    cax = fig.add_axes([0.91, 0.1, 0.015, 0.8])
    plt.colorbar(max, cax = cax) 

    plt.subplots_adjust(hspace=0.01,wspace=0.05)

    fig.savefig(file_name,dpi=600,bbox_inches='tight')

def Taylor_diagram_spatial_pattern_of_multiyear_climatology(obs_dataset, obs_name, model_datasets, model_names,
                                      file_name):

    # calculate climatological mean fields
    obs_dataset.values = utils.calc_temporal_mean(obs_dataset)
    for dataset in model_datasets:
        dataset.values = utils.calc_temporal_mean(dataset)

    # Metrics (spatial standard deviation and pattern correlation)
    # determine the metrics
    taylor_diagram = metrics.SpatialPatternTaylorDiagram()

    # create the Evaluation object
    taylor_evaluation = Evaluation(obs_dataset, # Reference dataset for the evaluation
                                 model_datasets, # list of target datasets for the evaluation
                                 [taylor_diagram])

    # run the evaluation (bias calculation)
    taylor_evaluation.run() 

    taylor_data = taylor_evaluation.results[0]

    plotter.draw_taylor_diagram(taylor_data, model_names, obs_name, file_name, pos='upper right',frameon=False)

def Time_series_subregion(obs_subregion_mean, obs_name, model_subregion_mean, model_names, seasonal_cycle, 
                          file_name, row, column, x_tick=['']):

    nmodel, nt, nregion = model_subregion_mean.shape  

    if seasonal_cycle:
        obs_data = ma.mean(obs_subregion_mean.reshape([1,nt/12,12,nregion]), axis=1)
        model_data = ma.mean(model_subregion_mean.reshape([nmodel,nt/12,12,nregion]), axis=1)
        nt = 12
    else:
        obs_data = obs_subregion_mean
        model_data = model_subregion_mean
        
    x_axis = np.arange(nt)
    x_tick_values = x_axis

    fig = plt.figure()
    rcParams['xtick.labelsize'] = 6
    rcParams['ytick.labelsize'] = 6
  
    for iregion in np.arange(nregion):
        ax = fig.add_subplot(row, column, iregion+1) 
        x_tick_labels = ['']
        if iregion+1  > column*(row-1):
            x_tick_labels = x_tick 
        else:
            x_tick_labels=['']
        ax.plot(x_axis, obs_data[0, :, iregion], color='r', lw=2, label=obs_name)
        for imodel in np.arange(nmodel):
            ax.plot(x_axis, model_data[imodel, :, iregion], lw=0.5, label = model_names[imodel])
        ax.set_xlim([-0.5,nt-0.5])
        ax.set_xticks(x_tick_values)
        ax.set_xticklabels(x_tick_labels)
        ax.set_title('Region %02d' % (iregion+1), fontsize=8)
    
    ax.legend(bbox_to_anchor=(-0.2, row/2), loc='center' , prop={'size':7}, frameon=False)  

    fig.subplots_adjust(hspace=0.7, wspace=0.5)
    fig.savefig(file_name, dpi=600, bbox_inches='tight')

def Portrait_diagram_subregion(obs_subregion_mean, obs_name, model_subregion_mean, model_names, seasonal_cycle,
                               file_name, normalize=True):

    nmodel, nt, nregion = model_subregion_mean.shape
    
    if seasonal_cycle:
        obs_data = ma.mean(obs_subregion_mean.reshape([1,nt/12,12,nregion]), axis=1)
        model_data = ma.mean(model_subregion_mean.reshape([nmodel,nt/12,12,nregion]), axis=1)
        nt = 12
    else:
        obs_data = obs_subregion_mean
        model_data = model_subregion_mean

    subregion_metrics = ma.zeros([4, nregion, nmodel])

    for imodel in np.arange(nmodel):
        for iregion in np.arange(nregion):
            # First metric: bias
            subregion_metrics[0, iregion, imodel] = metrics.calc_bias(model_data[imodel, :, iregion], obs_data[0, :, iregion], average_over_time = True)
            # Second metric: standard deviation
            subregion_metrics[1, iregion, imodel] = metrics.calc_stddev_ratio(model_data[imodel, :, iregion], obs_data[0, :, iregion])
            # Third metric: RMSE
            subregion_metrics[2, iregion, imodel] = metrics.calc_rmse(model_data[imodel, :, iregion], obs_data[0, :, iregion])
            # Fourth metric: correlation
            subregion_metrics[3, iregion, imodel] = metrics.calc_correlation(model_data[imodel, :, iregion], obs_data[0, :, iregion])
   
    if normalize:
        for iregion in np.arange(nregion):
            subregion_metrics[0, iregion, : ] = subregion_metrics[0, iregion, : ]/ma.std(obs_data[0, :, iregion])*100. 
            subregion_metrics[1, iregion, : ] = subregion_metrics[1, iregion, : ]*100. 
            subregion_metrics[2, iregion, : ] = subregion_metrics[2, iregion, : ]/ma.std(obs_data[0, :, iregion])*100. 

    region_names = ['R%02d' % i for i in np.arange(nregion)+1]

    for imetric, metric in enumerate(['bias','std','RMSE','corr']):
        plotter.draw_portrait_diagram(subregion_metrics[imetric, :, :], region_names, model_names, file_name+'_'+metric, 
                                      xlabel='model',ylabel='region')             

def Map_plot_subregion(subregions, ref_dataset, directory):
  
    lons, lats = np.meshgrid(ref_dataset.lons, ref_dataset.lats) 
    fig = plt.figure()
    ax = fig.add_subplot(111)
    m = Basemap(ax=ax, projection='cyl',llcrnrlat = lats.min(), urcrnrlat = lats.max(),
                llcrnrlon = lons.min(), urcrnrlon = lons.max(), resolution = 'l')
    m.drawcoastlines(linewidth=0.75)
    m.drawcountries(linewidth=0.75)
    m.etopo()  
    x, y = m(lons, lats) 
    #subregion_array = ma.masked_equal(subregion_array, 0)
    #max=m.contourf(x, y, subregion_array, alpha=0.7, cmap='Accent')
    for subregion in subregions:
        draw_screen_poly(subregion[1], m, 'w') 
        plt.annotate(subregion[0],xy=(0.5*(subregion[1][2]+subregion[1][3]), 0.5*(subregion[1][0]+subregion[1][1])), ha='center',va='center', fontsize=8) 
    fig.savefig(directory+'map_subregion', bbox_inches='tight')

def draw_screen_poly(boundary_array, m, linecolor='k'):

    ''' Draw a polygon on a map

    :param boundary_array: [lat_north, lat_south, lon_east, lon_west]
    :param m   : Basemap object
    '''

    lats = [boundary_array[0], boundary_array[0], boundary_array[1], boundary_array[1]]
    lons = [boundary_array[3], boundary_array[2], boundary_array[2], boundary_array[3]]
    x, y = m( lons, lats )
    xy = zip(x,y)
    poly = Polygon( xy, facecolor='none',edgecolor=linecolor )
    plt.gca().add_patch(poly)
    
    
   

    

    
