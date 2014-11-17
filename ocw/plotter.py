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
    :type name: :mod:`string`
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
    mn = mstats.scoreatpercentile(data, 5)
    mx = mstats.scoreatpercentile(data, 95)
    #if there min less than 0 and
    # or max more than 0 
    #put 0 in center of color bar
    if mn < 0 and mx > 0:
        level = max(abs(mn), abs(mx))
        mnlvl = -1 * level
        mxlvl = level
    #if min is larger than 0 then
    #have color bar between min and max
    else:
        mnlvl = mn
        mxlvl = mx
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
    ''' Draw a Taylor diagram.

    :param results: An Nx2 array containing normalized standard deviations,
       correlation coefficients, and names of evaluation results.
    :type results: :class:`numpy.ndarray`

    :param names: A list of names for each evaluated dataset
    :type names: :class:`list` of :mod:`string`

    :param refname: The name of the reference dataset.
    :type refname: :mod:`string`

    :param fname: The filename of the plot.
    :type fname: :mod:`string`

    :param fmt: (Optional) filetype for the output plot.
    :type fmt: :mod:`string`

    :param gridshape: (Optional) Tuple denoting the desired grid shape
        (num_rows, num_cols) for arranging the subplots.
    :type gridshape: A :class:`tuple` of the form (num_rows, num_cols)

    :param ptitle: (Optional) plot title.
    :type ptitle: :mod:`string`
    
    :param subtitles: (Optional) list of strings specifying the title for each
        subplot.
    :type subtitles: :class:`list` of :mod:`string`

    :param pos: (Optional) string or tuple of floats used to set the position
        of the legend. Check the `Matplotlib docs <http://matplotlib.org/api/legend_api.html#matplotlib.legend.Legend>`_
        for additional information.
    :type pos: :mod:`string` or :func:`tuple` of :class:`float`

    :param frameon: (Optional) boolean specifying whether to draw a frame
        around the legend box.
    :type frameon: :class:`bool`

    :param radmax: (Optional) float to adjust the extent of the axes in terms of
        standard deviation.
    :type radmax: :class:`float`
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
        # Convert rect to string form as expected by TaylorDiagram constructor
        rect = str(rect[0]) + str(rect[1]) + str(rect[2])

        # Create Taylor Diagram object
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
    ''' Draw subregion domain(s) on a map.

    :param subregions: The subregion objects to plot on the map.
    :type subregions: :class:`list` of subregion objects

    :param lats: Array of latitudes values.
    :type lats: :class:`numpy.ndarray`

    :param lons: Array of longitudes values.
    :type lons: :class:`numpy.ndarray`

    :param fname: The filename of the plot.
    :type fname: :mod:`string`

    :param fmt: (Optional) filetype for the output.
    :type fmt: :mod:`string`

    :param ptitle: (Optional) plot title.
    :type ptitle: :mod:`string`

    :param parallels: (Optional) :class:`list` of :class:`int` or :class:`float` for the parallels to
        be drawn. See the `Basemap documentation <http://matplotlib.org/basemap/users/graticule.html>`_
        for additional information.
    :type parallels: :class:`list` of :class:`int` or :class:`float`

    :param meridians: (Optional) :class:`list` of :class:`int` or :class:`float` for the meridians to
        be drawn. See the `Basemap documentation <http://matplotlib.org/basemap/users/graticule.html>`_
        for additional information.
    :type meridians: :class:`list` of :class:`int` or :class:`float`

    :param subregion_masks: (Optional) :class:`dict` of :class:`bool` arrays for each
        subregion for giving finer control of the domain to be drawn, by default
        the entire domain is drawn.
    :type subregion_masks: :class:`dict` of :class:`bool` arrays
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
    ''' Draw a time series plot.

    :param results: 3D array of time series data.
    :type results: :class:`numpy.ndarray`

    :param times: List of Python datetime objects used by Matplotlib to handle
        axis formatting.
    :type times: :class:`list` of :class:`datetime.datetime`

    :param labels: List of names for each data being plotted.
    :type labels: :class:`list` of :mod:`string`

    :param fname: Filename of the plot.
    :type fname: :mod:`string`

    :param fmt: (Optional) filetype for the output.
    :type fmt: :mod:`string`

    :param gridshape: (Optional) tuple denoting the desired grid shape
        (num_rows, num_cols) for arranging the subplots.
    :type gridshape: :func:`tuple` of the form (num_rows, num_cols)

    :param xlabel: (Optional) x-axis title.
    :type xlabel: :mod:`string`
    
    :param ylabel: (Optional) y-ayis title.
    :type ylabel: :mod:`string`

    :param ptitle: (Optional) plot title.
    :type ptitle: :mod:`string`

    :param subtitles: (Optional) list of titles for each subplot.
    :type subtitles: :class:`list` of :mod:`string`
    
    :param label_month: (Optional) flag to toggle drawing month labels on the
        x-axis.
    :type label_month: :class:`bool`

    :param yscale: (Optional) y-axis scale value, 'linear' for linear and 'log'
        for log base 10.
    :type yscale: :mod:`string`
    
    :param aspect: (Optional) approximate aspect ratio of each subplot
        (width / height). Default is 8.5 / 5.5
    :type aspect: :class:`float`
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
    ''' Draw a multiple panel contour map plot.

    :param dataset: 3D array of data to be plotted with shape (nT, nLon, nLat).
    :type dataset: :class:`numpy.ndarray`

    :param lats: Array of latitudes values.
    :type lats: :class:`numpy.ndarray`

    :param lons: Array of longitudes
    :type lons: :class:`numpy.ndarray`

    :param fname: The filename of the plot.
    :type fname: :mod:`string`

    :param fmt: (Optional) filetype for the output.
    :type fmt: :mod:`string`

    :param gridshape: (Optional) tuple denoting the desired grid shape
        (num_rows, num_cols) for arranging the subplots.
    :type gridshape: :func:`tuple` of the form (num_rows, num_cols)

    :param clabel: (Optional) colorbar title.
    :type clabel: :mod:`string`

    :param ptitle: (Optional) plot title.
    :type ptitle: :mod:`string`

    :param subtitles: (Optional) list of titles for each subplot.
    :type subtitles: :class:`list` of :mod:`string`

    :param cmap: (Optional) string or :class:`matplotlib.colors.LinearSegmentedColormap`
        instance denoting the colormap. This must be able to be recognized by
        `Matplotlib's get_cmap function <http://matplotlib.org/api/cm_api.html#matplotlib.cm.get_cmap>`_.
    :type cmap: :mod:`string` or :class:`matplotlib.colors.LinearSegmentedColormap`

    :param clevs: (Optional) contour levels values.
    :type clevs: :class:`list` of :class:`int` or :class:`float`
    
    :param nlevs: (Optional) target number of contour levels if clevs is None.
    :type nlevs: :class:`int`

    :param parallels: (Optional) list of ints or floats for the parallels to
        be drawn. See the `Basemap documentation <http://matplotlib.org/basemap/users/graticule.html>`_
        for additional information.
    :type parallels: :class:`list` of :class:`int` or :class:`float`

    :param meridians: (Optional) list of ints or floats for the meridians to
        be drawn. See the `Basemap documentation <http://matplotlib.org/basemap/users/graticule.html>`_
        for additional information.
    :type meridians: :class:`list` of :class:`int` or :class:`float`

    :param extend: (Optional) flag to toggle whether to place arrows at the colorbar
         boundaries. Default is 'neither', but can also be 'min', 'max', or
         'both'. Will be automatically set to 'both' if clevs is None.
    :type extend: :mod:`string`
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
    cbar = fig.colorbar(cs, cax=ax.cax, drawedges=True, orientation='horizontal', extendfrac='auto')
    cbar.set_label(clabel)
    cbar.set_ticks(clevs)
    cbar.ax.tick_params(labelsize=6)
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
    ''' Draw a portrait diagram plot.

    :param results: 3D array of the fields to be plotted. The second dimension
              should correspond to the number of rows in the diagram and the
              third should correspond to the number of columns.
    :type results: :class:`numpy.ndarray`

    :param rowlabels: Labels for each row.
    :type rowlabels: :class:`list` of :mod:`string`

    :param collabels: Labels for each row.
    :type collabels: :class:`list` of :mod:`string`

    :param fname: Filename of the plot.
    :type fname: :mod:`string`
    
    :param fmt: (Optional) filetype for the output.
    :type fmt: :mod:`string`

    :param gridshape: (Optional) tuple denoting the desired grid shape
        (num_rows, num_cols) for arranging the subplots.
    :type gridshape: :func:`tuple` of the form (num_rows, num_cols)

    :param xlabel: (Optional) x-axis title.
    :type xlabel: :mod:`string`

    :param ylabel: (Optional) y-ayis title.
    :type ylabel: :mod:`string`

    :param clabel: (Optional) colorbar title.
    :type clabel: :mod:`string`

    :param ptitle: (Optional) plot title.
    :type ptitle: :mod:`string`

    :param subtitles: (Optional) list of titles for each subplot.
    :type subtitles: :class:`list` of :mod:`string`

    :param cmap: (Optional) string or :class:`matplotlib.colors.LinearSegmentedColormap`
        instance denoting the colormap. This must be able to be recognized by
        `Matplotlib's get_cmap function <http://matplotlib.org/api/cm_api.html#matplotlib.cm.get_cmap>`_.
    :type cmap: :mod:`string` or :class:`matplotlib.colors.LinearSegmentedColormap`

    :param clevs: (Optional) contour levels values.
    :type clevs: :class:`list` of :class:`int` or :class:`float`

    :param nlevs: Optional target number of contour levels if clevs is None.
    :type nlevs: :class:`int`

    :param extend: (Optional) flag to toggle whether to place arrows at the colorbar
         boundaries. Default is 'neither', but can also be 'min', 'max', or
         'both'. Will be automatically set to 'both' if clevs is None.
    :type extend: :mod:`string`

    :param aspect: (Optional) approximate aspect ratio of each subplot
        (width / height). Default is 8.5 / 5.5
    :type aspect: :class:`float`
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
    cbar.ax.tick_params(labelsize=6)
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

class TaylorDiagram(object):
    """ Taylor diagram helper class

    Plot model standard deviation and correlation to reference (data)
    sample in a single-quadrant polar plot, with r=stddev and
    theta=arccos(correlation).

    This class was released as public domain by the original author
    Yannick Copin. You can find the original Gist where it was
    released at: https://gist.github.com/ycopin/3342888
    """

    def __init__(self, refstd, radmax=1.5, fig=None, rect=111, label='_'):
        """Set up Taylor diagram axes, i.e. single quadrant polar
        plot, using mpl_toolkits.axisartist.floating_axes. refstd is
        the reference standard deviation to be compared to.
        """

        from matplotlib.projections import PolarAxes
        import mpl_toolkits.axisartist.floating_axes as FA
        import mpl_toolkits.axisartist.grid_finder as GF

        self.refstd = refstd            # Reference standard deviation

        tr = PolarAxes.PolarTransform()

        # Correlation labels
        rlocs = np.concatenate((np.arange(10)/10.,[0.95,0.99]))
        tlocs = np.arccos(rlocs)        # Conversion to polar angles
        gl1 = GF.FixedLocator(tlocs)    # Positions
        tf1 = GF.DictFormatter(dict(zip(tlocs, map(str,rlocs))))

        # Standard deviation axis extent
        self.smin = 0
        self.smax = radmax*self.refstd

        ghelper = FA.GridHelperCurveLinear(tr,
                                           extremes=(0,np.pi/2, # 1st quadrant
                                                     self.smin,self.smax),
                                           grid_locator1=gl1,
                                           tick_formatter1=tf1,
                                           )

        if fig is None:
            fig = plt.figure()

        ax = FA.FloatingSubplot(fig, rect, grid_helper=ghelper)
        fig.add_subplot(ax)

        # Adjust axes
        ax.axis["top"].set_axis_direction("bottom")  # "Angle axis"
        ax.axis["top"].toggle(ticklabels=True, label=True)
        ax.axis["top"].major_ticklabels.set_axis_direction("top")
        ax.axis["top"].label.set_axis_direction("top")
        ax.axis["top"].label.set_text("Correlation")

        ax.axis["left"].set_axis_direction("bottom") # "X axis"
        ax.axis["left"].label.set_text("Standard deviation")

        ax.axis["right"].set_axis_direction("top")   # "Y axis"
        ax.axis["right"].toggle(ticklabels=True)
        ax.axis["right"].major_ticklabels.set_axis_direction("left")

        ax.axis["bottom"].set_visible(False)         # Useless

        # Contours along standard deviations
        ax.grid(False)

        self._ax = ax                   # Graphical axes
        self.ax = ax.get_aux_axes(tr)   # Polar coordinates

        # Add reference point and stddev contour
        # print "Reference std:", self.refstd
        l, = self.ax.plot([0], self.refstd, 'k*',
                          ls='', ms=10, label=label)
        t = np.linspace(0, np.pi/2)
        r = np.zeros_like(t) + self.refstd
        self.ax.plot(t,r, 'k--', label='_')

        # Collect sample points for latter use (e.g. legend)
        self.samplePoints = [l]

    def add_sample(self, stddev, corrcoef, *args, **kwargs):
        """Add sample (stddev,corrcoeff) to the Taylor diagram. args
        and kwargs are directly propagated to the Figure.plot
        command."""

        l, = self.ax.plot(np.arccos(corrcoef), stddev,
                          *args, **kwargs) # (theta,radius)
        self.samplePoints.append(l)

        return l

    def add_rms_contours(self, levels=5, **kwargs):
        """Add constant centered RMS difference contours."""

        rs,ts = np.meshgrid(np.linspace(self.smin,self.smax),
                            np.linspace(0,np.pi/2))
        # Compute centered RMS difference
        rms = np.sqrt(self.refstd**2 + rs**2 - 2*self.refstd*rs*np.cos(ts))

        contours = self.ax.contour(ts, rs, rms, levels, **kwargs)

    def add_stddev_contours(self, std, corr1, corr2, **kwargs):
        """Add a curved line with a radius of std between two points
        [std, corr1] and [std, corr2]"""

        t = np.linspace(np.arccos(corr1), np.arccos(corr2))
        r = np.zeros_like(t) + std
        return self.ax.plot(t,r,'red', linewidth=2)

    def add_contours(self,std1,corr1,std2,corr2, **kwargs):
        """Add a line between two points
        [std1, corr1] and [std2, corr2]"""

        t = np.linspace(np.arccos(corr1), np.arccos(corr2))
        r = np.linspace(std1, std2)

        return self.ax.plot(t,r,'red',linewidth=2)
