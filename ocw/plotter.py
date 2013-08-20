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

from tempfile import TemporaryFile
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1 import ImageGrid
import scipy.stats.mstats as mstats
import numpy as np
import numpy.ma as ma
from utils.taylor import TaylorDiagram

# Set the default colormap to coolwarm
mpl.rc('image', cmap='coolwarm')

def set_cmap(name):
    '''
    Sets the default colormap (eg when setting cmap=None in a function)
    See: http://matplotlib.org/examples/pylab_examples/show_colormaps.html
    for a list of possible colormaps.
    Appending '_r' to a matplotlib colormap name will give you a reversed
    version of it.
    
    :param name: The name of the colormap.
    :type name: str
    '''
    # The first line is redundant but it prevents the user from setting
    # the cmap rc value improperly
    cmap = plt.get_cmap(name)
    mpl.rc('image', cmap=cmap.name)
    
def _nice_intervals(data, nlevs):
    '''
    Purpose::
        Calculates nice intervals between each color level for colorbars
        and contour plots. The target minimum and maximum color levels are
        calculated by taking the minimum and maximum of the distribution
        after cutting off the tails to remove outliers. 
    
    Input::
        data - an array of data to be plotted
        nlevs - an int giving the target number of intervals
        
    Output::
        clevs - A list of floats for the resultant colorbar levels
    '''
    # Find the min and max levels by cutting off the tails of the distribution
    # This mitigates the influence of outliers
    data = data.ravel()
    mnlvl = mstats.scoreatpercentile(data, 5)
    mxlvl = mstats.scoreatpercentile(data, 95)
    locator = mpl.ticker.MaxNLocator(nlevs)
    clevs = locator.tick_values(mnlvl, mxlvl)
    
    # Make sure the bounds of clevs are reasonable since sometimes
    # MaxNLocator gives values outside the domain of the input data
    clevs = clevs[(clevs >= mnlvl) & (clevs <= mxlvl)]
    return clevs

def _best_grid_shape(nplots, oldshape):
    '''
    Purpose::
        Calculate a better grid shape in case the user enters more columns
        and rows than needed to fit a given number of subplots.
        
    Input::
        nplots - an int giving the number of plots that will be made
        oldshape - a tuple denoting the desired grid shape (nrows, ncols) for arranging
                    the subplots originally requested by the user. 
    
    Output::
        newshape - the smallest possible subplot grid shape needed to fit nplots
    '''
    nrows, ncols = oldshape
    size = nrows * ncols
    diff = size - nplots
    if diff < 0:
        raise ValueError('gridshape=(%d, %d): Cannot fit enough subplots for data' %(nrows, ncols))
    else:
        # If the user enters an excessively large number of
        # rows and columns for gridshape, automatically
        # correct it so that it fits only as many plots
        # as needed
        while diff >= ncols:
            nrows -= 1
            size = nrows * ncols
            diff = size - nplots
            
        # Don't forget to remove unnecessary columns too
        if nrows == 1:
            ncols = nplots
            
        newshape = nrows, ncols
        return newshape
    
def _fig_size(gridshape, aspect=None):
    '''
    Purpose::
        Calculates the figure dimensions from a subplot gridshape
        
    Input::
        gridshape - Tuple denoting the subplot gridshape
        aspect - Float denoting approximate aspect ratio of each subplot 
                 (width / height). Default is 8.5 / 5.5
        
    Output::
        width - float for width of the figure in inches
        height - float for height of the figure in inches
    '''
    if aspect is None:
        aspect = 8.5 / 5.5

    # Default figure size is 8.5" x 5.5" if nrows == ncols
    # and then adjusted by given aspect ratio
    nrows, ncols = gridshape
    if nrows >= ncols:
        # If more rows keep width constant
        width, height = (aspect * 5.5), 5.5 * (nrows / ncols)
    else:
        # If more columns keep height constant
        width, height = (aspect * 5.5) * (ncols / nrows), 5.5
        
    return width, height
    
def draw_taylor_diagram(results, names, refname, fname, fmt='png', 
                        gridshape=(1,1), ptitle='', subtitles=None, 
                        pos='upper right', frameon=True, radmax=1.5):
    '''
    Purpose::
        Draws a Taylor diagram
        
    Input::
        results - an Nx2 array containing normalized standard deviations,
               correlation coefficients, and names of evaluation results
        names - list of names for each evaluated dataset
        refname - The name of the reference dataset
        fname  - a string specifying the filename of the plot
        fmt  - an optional string specifying the filetype, default is .png
        gridshape - optional tuple denoting the desired grid shape (nrows, ncols) for arranging
                    the subplots. 
        ptitle - an optional string specifying the plot title
        subtitles - an optional list of strings specifying the title for each subplot
        pos - an optional string or tuple of float for determining 
                    the position of the legend
        frameon - an optional boolean that determines whether to draw a frame
                        around the legend box
        radmax - an optional float to adjust the extent of the axes in terms of
                 standard deviation.
    '''
    # Handle the single plot case. 
    if results.ndim == 2:
        results = results.reshape(1, *results.shape)

    # Make sure gridshape is compatible with input data
    nplots = results.shape[0]
    gridshape = _best_grid_shape(nplots, gridshape)
    
    # Set up the figure
    fig = plt.figure()
    fig.set_size_inches((8.5, 11))
    fig.dpi = 300
    for i, data in enumerate(results):
        rect = gridshape + (i + 1,)
        dia = TaylorDiagram(1, fig=fig, rect=rect, label=refname, radmax=radmax)
        for i, (stddev, corrcoef) in enumerate(data):
            dia.add_sample(stddev, corrcoef, marker='$%d$' % (i + 1), ms=6, 
                           label=names[i])
            if subtitles is not None:
                dia._ax.set_title(subtitles[i])
    
    # Add legend
    legend = fig.legend(dia.samplePoints, 
                        [p.get_label() for p in dia.samplePoints], 
                        handlelength=0., prop={'size': 10}, numpoints=1, 
                        loc=pos)
    legend.draw_frame(frameon)
    plt.subplots_adjust(wspace=0)          
    
    # Add title and save the figure
    fig.suptitle(ptitle)
    plt.tight_layout(.05, .05)
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi)    
    fig.clf()
    
def draw_subregions(subregions, lats, lons, fname, fmt='png', ptitle='',
                    parallels=None, meridians=None, subregion_masks=None):
    '''
    Purpose::
        Function to draw subregion domain(s) on a map
        
    Input::
        subregions - a list of subRegion objects
        lats - array of latitudes
        lons - array of longitudes
        fname  - a string specifying the filename of the plot
        fmt  - an optional string specifying the filetype, default is .png
        ptitle - an optional string specifying plot title
        parallels - an optional list of ints or floats for the parallels to be drawn 
        meridians - an optional list of ints or floats for the meridians to be drawn
        subregion_masks - optional dictionary of boolean arrays for each subRegion
                         for giving finer control of the domain to be drawn, by default
                         the entire domain is drawn. 
    '''
    # Set up the figure
    fig = plt.figure()
    fig.set_size_inches((8.5, 11.))
    fig.dpi = 300
    ax = fig.add_subplot(111)
    
    # Determine the map boundaries and construct a Basemap object
    lonmin = lons.min()
    lonmax = lons.max()
    latmin = lats.min()
    latmax = lats.max()
    m = Basemap(projection='cyl', llcrnrlat=latmin, urcrnrlat=latmax,
                llcrnrlon=lonmin, urcrnrlon=lonmax, resolution='l', ax=ax)
    
    # Draw the borders for coastlines and countries
    m.drawcoastlines(linewidth=1)
    m.drawcountries(linewidth=.75)
    m.drawstates()
    
    # Create default meridians and parallels. The interval between
    # them should be 1, 5, 10, 20, 30, or 40 depending on the size
    # of the domain
    length = max((latmax - latmin), (lonmax - lonmin)) / 5
    if length <= 1:
        dlatlon = 1
    elif length <= 5:
        dlatlon = 5
    else:
        dlatlon = np.round(length, decimals=-1)
        
    if meridians is None:
        meridians = np.r_[np.arange(0, -180, -dlatlon)[::-1], np.arange(0, 180, dlatlon)]
    if parallels is None:
        parallels = np.r_[np.arange(0, -90, -dlatlon)[::-1], np.arange(0, 90, dlatlon)]
        
    # Draw parallels / meridians
    m.drawmeridians(meridians, labels=[0, 0, 0, 1], linewidth=.75, fontsize=10)
    m.drawparallels(parallels, labels=[1, 0, 0, 1], linewidth=.75, fontsize=10)

    # Set up the color scaling
    cmap = plt.cm.rainbow
    norm = mpl.colors.BoundaryNorm(np.arange(1, len(subregions) + 3), cmap.N)
    
    # Process the subregions 
    for i, reg in enumerate(subregions):
        if subregion_masks is not None and reg.name in subregion_masks.keys():
            domain = (i + 1) * subregion_masks[reg.name]
        else:        
            domain = (i + 1) * np.ones((2, 2))
        
        nlats, nlons = domain.shape
        domain = ma.masked_equal(domain, 0)
        reglats = np.linspace(reg.latmin, reg.latmax, nlats)
        reglons = np.linspace(reg.lonmin, reg.lonmax, nlons)            
        reglons, reglats = np.meshgrid(reglons, reglats)
        
        # Convert to to projection coordinates. Not really necessary
        # for cylindrical projections but keeping it here in case we need
        # support for other projections.
        x, y = m(reglons, reglats)
        
        # Draw the subregion domain
        m.pcolormesh(x, y, domain, cmap=cmap, norm=norm, alpha=.5)
        
        # Label the subregion
        xm, ym = x.mean(), y.mean()
        m.plot(xm, ym, marker='$%s$' %(reg.name), markersize=12, color='k')
    
    # Add the title
    ax.set_title(ptitle)
    
    # Save the figure
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi)
    fig.clf()

def draw_time_series(results, times, labels, fname, fmt='png', gridshape=(1, 1), 
                     xlabel='', ylabel='', ptitle='', subtitles=None, 
                     label_month=False, yscale='linear', aspect=None):
    '''
    Purpose::
        Function to draw a time series plot
     
    Input:: 
        results - a 3d array of time series
        times - a list of python datetime objects
        labels - a list of strings with the names of each set of data
        fname - a string specifying the filename of the plot
        fmt - an optional string specifying the output filetype
        gridshape - optional tuple denoting the desired grid shape (nrows, ncols) for arranging
                    the subplots. 
        xlabel - a string specifying the x-axis title
        ylabel - a string specifying the y-axis title
        ptitle - a string specifying the plot title
        subtitles - an optional list of strings specifying the title for each subplot
        label_month - optional bool to toggle drawing month labels
        yscale - optional string for setting the y-axis scale, 'linear' for linear
                 and 'log' for log base 10.
        aspect - Float denoting approximate aspect ratio of each subplot 
                 (width / height). Default is 8.5 / 5.5
    '''
    # Handle the single plot case. 
    if results.ndim == 2:
        results = results.reshape(1, *results.shape)

    # Make sure gridshape is compatible with input data
    nplots = results.shape[0]
    gridshape = _best_grid_shape(nplots, gridshape)
        
    # Set up the figure
    width, height = _fig_size(gridshape)
    fig = plt.figure()
    fig.set_size_inches((width, height))
    fig.dpi = 300
    
    # Make the subplot grid
    grid = ImageGrid(fig, 111,
                     nrows_ncols=gridshape,
                     axes_pad=0.3,
                     share_all=True,
                     add_all=True,
                     ngrids=nplots,
                     label_mode='L',
                     aspect=False,
                     cbar_mode='single',
                     cbar_location='bottom',
                     cbar_size=.05,
                     cbar_pad=.20
                     )
    
    # Make the plots
    for i, ax in enumerate(grid):
        data = results[i]
        if label_month:
            xfmt = mpl.dates.DateFormatter('%b')
            xloc = mpl.dates.MonthLocator()
            ax.xaxis.set_major_formatter(xfmt)
            ax.xaxis.set_major_locator(xloc)
    
        # Set the y-axis scale
        ax.set_yscale(yscale)
    
        # Set up list of lines for legend
        lines = []
        ymin, ymax = 0, 0
                
        # Plot each line
        for tSeries in data:
            line = ax.plot_date(times, tSeries, '')
            lines.extend(line)
            cmin, cmax = tSeries.min(), tSeries.max()
            ymin = min(ymin, cmin)
            ymax = max(ymax, cmax)
            
        # Add a bit of padding so lines don't touch bottom and top of the plot
        ymin = ymin - ((ymax - ymin) * 0.1)
        ymax = ymax + ((ymax - ymin) * 0.1)
        ax.set_ylim((ymin, ymax))
        
        # Set the subplot title if desired
        if subtitles is not None:
            ax.set_title(subtitles[i], fontsize='small')
        
    # Create a master axes rectangle for figure wide labels
    fax = fig.add_subplot(111, frameon=False)
    fax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    fax.set_ylabel(ylabel)
    fax.set_title(ptitle, fontsize=16)
    fax.title.set_y(1.04)
    
    # Create the legend using a 'fake' colorbar axes. This lets us have a nice
    # legend that is in sync with the subplot grid
    cax = ax.cax
    cax.set_frame_on(False)
    cax.set_xticks([])
    cax.set_yticks([])
    cax.legend((lines), labels, loc='upper center', ncol=10, fontsize='small', 
                   mode='expand', frameon=False)
    
    # Note that due to weird behavior by axes_grid, it is more convenient to
    # place the x-axis label relative to the colorbar axes instead of the
    # master axes rectangle.
    cax.set_title(xlabel, fontsize=12)
    cax.title.set_y(-1.5)
    
    # Rotate the x-axis tick labels
    for ax in grid:
        for xtick in ax.get_xticklabels():
            xtick.set_ha('right')
            xtick.set_rotation(30)
    
    # Save the figure
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi)
    fig.clf()

def draw_contour_map(dataset, lats, lons, fname, fmt='png', gridshape=(1, 1),
                     clabel='', ptitle='', subtitles=None, cmap=None, 
                     clevs=None, nlevs=10, parallels=None, meridians=None,
                     extend='neither', aspect=8.5/2.5):
    '''
    Purpose::
        Create a multiple panel contour map plot.
       
    Input::
        dataset -  3d array of the field to be plotted with shape (nT, nLon, nLat)
        lats - array of latitudes
        lons - array of longitudes
        fname  - a string specifying the filename of the plot
        fmt  - an optional string specifying the filetype, default is .png
        gridshape - optional tuple denoting the desired grid shape (nrows, ncols) for arranging
                    the subplots. 
        clabel - an optional string specifying the colorbar title
        ptitle - an optional string specifying plot title
        subtitles - an optional list of strings specifying the title for each subplot
        cmap - an string or optional matplotlib.colors.LinearSegmentedColormap instance
               denoting the colormap
        clevs - an optional list of ints or floats specifying contour levels
        nlevs - an optional integer specifying the target number of contour levels if
                clevs is None        
        parallels - an optional list of ints or floats for the parallels to be drawn 
        meridians - an optional list of ints or floats for the meridians to be drawn
        extend - an optional string to toggle whether to place arrows at the colorbar
             boundaries. Default is 'neither', but can also be 'min', 'max', or
             'both'. Will be automatically set to 'both' if clevs is None.     
    '''
    # Handle the single plot case. Meridians and Parallels are not labeled for
    # multiple plots to save space.
    if dataset.ndim == 2 or (dataset.ndim == 3 and dataset.shape[0] == 1):
        if dataset.ndim == 2:
            dataset = dataset.reshape(1, *dataset.shape)
        mlabels = [0, 0, 0, 1]
        plabels = [1, 0, 0, 1]
    else:
        mlabels = [0, 0, 0, 0]
        plabels = [0, 0, 0, 0]
        
    # Make sure gridshape is compatible with input data
    nplots = dataset.shape[0]
    gridshape = _best_grid_shape(nplots, gridshape)
        
    # Set up the figure
    fig = plt.figure()
    fig.set_size_inches((8.5, 11.))
    fig.dpi = 300
    
    # Make the subplot grid
    grid = ImageGrid(fig, 111,
                     nrows_ncols=gridshape,
                     axes_pad=0.3,
                     share_all=True,
                     add_all=True,
                     ngrids=nplots,
                     label_mode='L',
                     cbar_mode='single',
                     cbar_location='bottom',
                     cbar_size=.15,
                     cbar_pad='0%'
                     )
        
    # Determine the map boundaries and construct a Basemap object
    lonmin = lons.min()
    lonmax = lons.max()
    latmin = lats.min()
    latmax = lats.max()
    m = Basemap(projection = 'cyl', llcrnrlat = latmin, urcrnrlat = latmax,
                llcrnrlon = lonmin, urcrnrlon = lonmax, resolution = 'l')
    
    # Convert lats and lons to projection coordinates
    if lats.ndim == 1 and lons.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    
    # Calculate contour levels if not given
    if clevs is None:
        # Cut off the tails of the distribution
        # for more representative contour levels
        clevs = _nice_intervals(dataset, nlevs)
        extend = 'both'
    
    cmap = plt.get_cmap(cmap)
    
    # Create default meridians and parallels. The interval between
    # them should be 1, 5, 10, 20, 30, or 40 depending on the size
    # of the domain
    length = max((latmax - latmin), (lonmax - lonmin)) / 5
    if length <= 1:
        dlatlon = 1
    elif length <= 5:
        dlatlon = 5
    else:
        dlatlon = np.round(length, decimals = -1)
    if meridians is None:
        meridians = np.r_[np.arange(0, -180, -dlatlon)[::-1], np.arange(0, 180, dlatlon)]
    if parallels is None:
        parallels = np.r_[np.arange(0, -90, -dlatlon)[::-1], np.arange(0, 90, dlatlon)]
            
    x, y = m(lons, lats)
    for i, ax in enumerate(grid):        
        # Load the data to be plotted
        data = dataset[i]
        m.ax = ax
        
        # Draw the borders for coastlines and countries
        m.drawcoastlines(linewidth=1)
        m.drawcountries(linewidth=.75)
        
        # Draw parallels / meridians
        m.drawmeridians(meridians, labels=mlabels, linewidth=.75, fontsize=10)
        m.drawparallels(parallels, labels=plabels, linewidth=.75, fontsize=10)
        
        # Draw filled contours
        cs = m.contourf(x, y, data, cmap=cmap, levels=clevs, extend=extend)
        
        # Add title
        if subtitles is not None:
            ax.set_title(subtitles[i], fontsize='small')

    # Add colorbar
    cbar = fig.colorbar(cs, cax=ax.cax, drawedges=True, orientation='horizontal',
                        extendfrac='auto')
    cbar.set_label(clabel)
    cbar.set_ticks(clevs)
    cbar.ax.xaxis.set_ticks_position('none')
    cbar.ax.yaxis.set_ticks_position('none')
        
    # This is an ugly hack to make the title show up at the correct height.
    # Basically save the figure once to achieve tight layout and calculate
    # the adjusted heights of the axes, then draw the title slightly above
    # that height and save the figure again
    fig.savefig(TemporaryFile(), bbox_inches='tight', dpi=fig.dpi)
    ymax = 0
    for ax in grid:
        bbox = ax.get_position()
        ymax = max(ymax, bbox.ymax)
    
    # Add figure title
    fig.suptitle(ptitle, y=ymax + .06, fontsize=16)
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi)
    fig.clf()

def draw_portrait_diagram(results, rowlabels, collabels, fname, fmt='png', 
                          gridshape=(1, 1), xlabel='', ylabel='', clabel='', 
                          ptitle='', subtitles=None, cmap=None, clevs=None, 
                          nlevs=10, extend='neither', aspect=None):
    '''
    Purpose::
        Makes a portrait diagram plot.
        
    Input::
        results - 3d array of the field to be plotted. The second dimension 
                  should correspond to the number of rows in the diagram and the
                  third should correspond to the number of columns.
        rowlabels - a list of strings denoting labels for each row
        collabels - a list of strings denoting labels for each column
        fname - a string specifying the filename of the plot
        fmt - an optional string specifying the output filetype
        gridshape - optional tuple denoting the desired grid shape (nrows, ncols) for arranging
                    the subplots. 
        xlabel - an optional string specifying the x-axis title
        ylabel - an optional string specifying the y-axis title
        clabel - an optional string specifying the colorbar title
        ptitle - a string specifying the plot title
        subtitles - an optional list of strings specifying the title for each subplot
        cmap - an optional string or matplotlib.colors.LinearSegmentedColormap instance
               denoting the colormap
        clevs - an optional list of ints or floats specifying colorbar levels
        nlevs - an optional integer specifying the target number of contour levels if
                clevs is None        
        extend - an optional string to toggle whether to place arrows at the colorbar
             boundaries. Default is 'neither', but can also be 'min', 'max', or
             'both'. Will be automatically set to 'both' if clevs is None.     
        aspect - Float denoting approximate aspect ratio of each subplot 
                 (width / height). Default is 8.5 / 5.5
    '''  
    # Handle the single plot case.
    if results.ndim == 2:
        results = results.reshape(1, *results.shape)
    
    nplots = results.shape[0]
    
    # Make sure gridshape is compatible with input data
    gridshape = _best_grid_shape(nplots, gridshape)
    
    # Row and Column labels must be consistent with the shape of
    # the input data too
    prows, pcols = results.shape[1:]
    if len(rowlabels) != prows or len(collabels) != pcols:
        raise ValueError('rowlabels and collabels must have %d and %d elements respectively' %(prows, pcols))
     
    # Set up the figure
    width, height = _fig_size(gridshape)
    fig = plt.figure()
    fig.set_size_inches((width, height))
    fig.dpi = 300
    
    # Make the subplot grid
    grid = ImageGrid(fig, 111,
                     nrows_ncols=gridshape,
                     axes_pad=0.4,
                     share_all=True,
                     aspect=False,
                     add_all=True,
                     ngrids=nplots,
                     label_mode='all',
                     cbar_mode='single',
                     cbar_location='bottom',
                     cbar_size=.15,
                     cbar_pad='3%'
                     )
    
    # Calculate colorbar levels if not given
    if clevs is None:
        # Cut off the tails of the distribution
        # for more representative colorbar levels
        clevs = _nice_intervals(results, nlevs)
        extend = 'both'
        
    cmap = plt.get_cmap(cmap)    
    norm = mpl.colors.BoundaryNorm(clevs, cmap.N)
    
    # Do the plotting
    for i, ax in enumerate(grid):
        data = results[i]
        cs = ax.matshow(data, cmap=cmap, aspect='auto', origin='lower', norm=norm)
        
        # Add grid lines
        ax.xaxis.set_ticks(np.arange(data.shape[1] + 1))
        ax.yaxis.set_ticks(np.arange(data.shape[0] + 1))
        x = (ax.xaxis.get_majorticklocs() - .5)
        y = (ax.yaxis.get_majorticklocs() - .5)
        ax.vlines(x, y.min(), y.max())
        ax.hlines(y, x.min(), x.max())
        
        # Configure ticks
        ax.xaxis.tick_bottom()
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.set_xticklabels(collabels, fontsize='xx-small')
        ax.set_yticklabels(rowlabels, fontsize='xx-small')
        
        # Add axes title
        if subtitles is not None:
            ax.text(0.5, 1.04, subtitles[i], va='center', ha='center', 
                    transform = ax.transAxes, fontsize='small')
    
    # Create a master axes rectangle for figure wide labels
    fax = fig.add_subplot(111, frameon=False)
    fax.tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    fax.set_ylabel(ylabel)
    fax.set_title(ptitle, fontsize=16)
    fax.title.set_y(1.04)
    
    # Add colorbar
    cax = ax.cax
    cbar = fig.colorbar(cs, cax=cax, norm=norm, boundaries=clevs, drawedges=True, 
                        extend=extend, orientation='horizontal', extendfrac='auto')
    cbar.set_label(clabel)
    cbar.set_ticks(clevs)
    cbar.ax.xaxis.set_ticks_position('none')
    cbar.ax.yaxis.set_ticks_position('none')
    
    # Note that due to weird behavior by axes_grid, it is more convenient to
    # place the x-axis label relative to the colorbar axes instead of the
    # master axes rectangle.
    cax.set_title(xlabel, fontsize=12)
    cax.title.set_y(1.5)
    
    # Save the figure
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi)
    fig.clf()