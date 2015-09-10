#Apache OCW lib immports
import ocw.data_source.local as local
import ocw.plotter as plotter
import ocw.utils as utils
import ocw.evaluation as evaluation
import ocw.metrics as metrics

# Python libraries
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap 
import string

def Map_plot_bias_of_multiyear_climatology(obs_dataset, obs_name, model_datasets, model_names,
                                      file_name, row, column):
    obs_clim = utils.calc_temporal_mean(obs_dataset)
    model_clim = []
    for idata, dataset in enumerate(model_datasets):
        model_clim.append(utils.calc_temporal_mean(dataset))

    nmodel = len(model_names)
    ny, nx = obs_dataset.values.shape[1:]

    rcm_bias = ma.zeros([nmodel, ny, nx])

    for imodel in np.arange(nmodel):
        rcm_bias[imodel,:,:] = model_clim[imodel] - obs_clim

    fig = plt.figure()

    lat_min = obs_dataset.lats.min()
    lat_max = obs_dataset.lats.max()
    lon_min = obs_dataset.lons.min()
    lon_max = obs_dataset.lons.max()

    string_list = list(string.ascii_lowercase) 
    ax = fig.add_subplot(row,column,1)
    m = Basemap(ax=ax, projection ='cyl', llcrnrlat = lat_min, urcrnrlat = lat_max,
            llcrnrlon = lon_min, urcrnrlon = lon_max, resolution = 'l', fix_aspect=False)
    lons, lats = np.meshgrid(obs_dataset.lons, obs_dataset.lats)

    x,y = m(lons, lats)

    m.drawcoastlines(linewidth=1)
    m.drawcountries(linewidth=1)
    m.drawstates(linewidth=0.5, color='w')
    max = m.contourf(x,y,obs_clim,levels = plotter._nice_intervals(obs_dataset.values, 10), extend='both',cmap='PuOr')
    ax.annotate('(a) \n' + obs_name,xy=(lon_min, lat_min))
    cax = fig.add_axes([0.02, 1.-float(1./row), 0.01, 1./row*0.6])
    plt.colorbar(max, cax = cax) 
    clevs = plotter._nice_intervals(rcm_bias, 11)
    for imodel in np.arange(nmodel):
        ax = fig.add_subplot(row, column,2+imodel)
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

    plt.show()
    fig.savefig(file_name,dpi=600,bbox_inches='tight')

def Taylor_diagram_spatial_pattern_of_multiyear_climatology(obs_dataset, obs_name, model_datasets, model_names,
                                      file_name):
    obs = utils.calc_temporal_mean(obs_dataset)
    model_clim=[]
    for idata, dataset in enumerate(model_datasets):
        model_clim.append(utils.calc_temporal_mean(dataset))

    # Metrics (spatial standard deviation and pattern correlation)
    nmodel = len(model_names)
    taylor_data = np.zeros([nmodel, 2])

    for imodel in np.arange(nmodel):
        model = model_clim[imodel]
        taylor_data[imodel,0] = ma.std(model[(model.mask==False) & (obs.mask == False)])/ma.std(obs[(model.mask==False) & (obs.mask == False)])
        taylor_data[imodel,1] = ma.corrcoef(obs_dataset.values.flatten(), model_datasets[imodel].values.flatten())[0,1]

    plotter.draw_taylor_diagram(taylor_data, model_names, obs_name, file_name, pos='best',frameon=False)

