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
"""Module that handles the generation of data plots"""


# Import Statements

from math import floor, log
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
import numpy as np
import os

def pow_round(x):
    '''
     Function to round x to the nearest power of 10
    '''
    return 10 ** (floor(log(x, 10) - log(0.5, 10)))

def calc_nice_color_bar_values(mymin, mymax, target_nlevs):
    '''
     Function to help make nicer plots. 
     
     Calculates an appropriate min, max and number of intervals to use in a color bar 
     such that the labels come out as round numbers.
    
     i.e. often, the color bar labels will come out as  0.1234  0.2343 0.35747 0.57546
     when in fact you just want  0.1, 0.2, 0.3, 0.4, 0.5 etc
    
    
     Method::
         Adjusts the max,min and nlevels slightly so as to provide nice round numbers.
    
     Input::
        mymin        - minimum of data range (or first guess at minimum color bar value)
        mymax        - maximum of data range (or first guess at maximum color bar value)
        target_nlevs - approximate number of levels/color bar intervals you would like to have
    
     Output::
        newmin       - minimum value of color bar to use
        newmax       - maximum value of color bar to use
        new_nlevs    - number of intervals in color bar to use
        * when all of the above are used, the color bar should have nice round number labels.
    '''
    myrange = mymax - mymin
    # Find target color bar label interval, given target number of levels.
    #  NB. this is likely to be not a nice rounded number.
    target_interval = myrange / float(target_nlevs)
    
    # Find power of 10 that the target interval lies in
    nearest_ten = pow_round(target_interval)
    
    # Possible interval levels, 
    #  i.e.  labels of 1,2,3,4,5 etc are OK, 
    #        labels of 2,4,6,8,10 etc are OK too
    #        labels of 3,6,9,12 etc are NOT OK (as defined below)
    #  NB.  this is also true for any multiple of 10 of these values
    #    i.e.  0.01,0.02,0.03,0.04 etc are OK too.
    pos_interval_levels = np.array([1, 2, 5])
    
    # Find possible intervals to use within this power of 10 range
    candidate_intervals = (pos_interval_levels * nearest_ten)
    
    # Find which of the candidate levels is closest to the target level
    absdiff = abs(target_interval - candidate_intervals)
    
    rounded_interval = candidate_intervals[np.where(absdiff == min(absdiff))]
    
    # Define actual nlevels to use in colorbar
    nlevels = myrange / rounded_interval
    
    # Define the color bar labels
    newmin = mymin - mymin % rounded_interval
    
    all_labels = np.arange(newmin, mymax + rounded_interval, rounded_interval) 
    
    newmin = all_labels.min()  
    newmax = all_labels.max()
    
    new_nlevs = int(len(all_labels)) - 1
    
    return newmin, newmax, new_nlevs

def draw_cntr_map_single(pVar, lats, lons, mnLvl, mxLvl, pTitle, pName, pType = 'png', cMap = None):
    '''
    Purpose::
        Plots a filled contour map.
       
    Input::
        pVar - 2d array of the field to be plotted with shape (nLon, nLat)
        lon - array of longitudes 
        lat - array of latitudes
        mnLvl - an integer specifying the minimum contour level
        mxLvl - an integer specifying the maximum contour level
        pTitle - a string specifying plot title
        pName  - a string specifying the filename of the plot
        pType  - an optional string specifying the filetype, default is .png
        cMap - an optional matplotlib.LinearSegmentedColormap object denoting the colormap,
               default is matplotlib.pyplot.cm.jet

        TODO: Let user specify map projection, whether to mask bodies of water??
        
    '''
    if cMap is None:
        cMap = plt.cm.jet
        
    # Set up the figure
    fig = plt.figure()
    ax = fig.gca()

    # Determine the map boundaries and construct a Basemap object
    lonMin = lons.min()
    lonMax = lons.max()
    latMin = lats.min()
    latMax = lats.max()
    m = Basemap(projection = 'cyl', llcrnrlat = latMin, urcrnrlat = latMax,
            llcrnrlon = lonMin, urcrnrlon = lonMax, resolution = 'l', ax = ax)

    # Draw the borders for coastlines and countries
    m.drawcoastlines(linewidth = 1)
    m.drawcountries(linewidth = .75)
    
    # Draw 6 parallels / meridians.
    m.drawmeridians(np.linspace(lonMin, lonMax, 5), labels = [0, 0, 0, 1])
    m.drawparallels(np.linspace(latMin, latMax, 5), labels = [1, 0, 0, 1])

    # Convert lats and lons to projection coordinates
    if lats.ndim == 1 and lons.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    x, y = m(lons, lats)

    # Plot data with filled contours
    nsteps = 24
    mnLvl, mxLvl, nsteps = calc_nice_color_bar_values(mnLvl, mxLvl, nsteps)
    spLvl = (mxLvl - mnLvl) / nsteps
    clevs = np.arange(mnLvl, mxLvl, spLvl)
    cs = m.contourf(x, y, pVar, cmap = cMap)

    # Add a colorbar and save the figure
    cbar = m.colorbar(cs, ax = ax, pad = .05)
    plt.title(pTitle)
    fig.savefig('%s.%s' %(pName, pType))

def draw_time_series_plot(data, times, myfilename, myworkdir, data2='', mytitle='', ytitle='Y', xtitle='time', year_labels=True):
    '''
     Purpose::
         Function to draw a time series plot
     
     Input:: 
         data - a masked numpy array of data masked by missing values		
         times - a list of python datetime objects
         myfilename - stub of png file created e.g. 'myfile' -> myfile.png
         myworkdir - directory to save images in
         data2 - (optional) second data line to plot assumes same time values)
         mytitle - (optional) chart title
    	 xtitle - (optional) y-axis title
    	 ytitle - (optional) y-axis title
    
     Output::
         no data returned from function
         Image file produced with name {filename}.png
    '''
    print 'Producing time series plot'

    fig = plt.figure()
    ax = fig.gca()

    if year_labels == False:
        xfmt = mpl.dates.DateFormatter('%b')
        ax.xaxis.set_major_formatter(xfmt)

    # x-axis title
    plt.xlabel(xtitle)

    # y-axis title
    plt.ylabel(ytitle)

    # Main title
    fig.suptitle(mytitle, fontsize=12)

    # Set y-range to sensible values
    # NB. if plotting two lines, then make sure range appropriate for both datasets
    ymin = data.min()
    ymax = data.max()

    # If data2 has been passed in, then set plot range to fit both lines.
    # NB. if data2 has been passed in, then it is an array, otherwise it defaults to an empty string
    if type(data2) != str:
        ymin = min(data.min(), data2.min())
        ymax = max(data.max(), data2.max())

    # add a bit of padding so lines don't touch bottom and top of the plot
    ymin = ymin - ((ymax - ymin) * 0.1)
    ymax = ymax + ((ymax - ymin) * 0.1)

    # Set y-axis range
    plt.ylim((ymin, ymax))

    # Make plot, specifying marker style ('x'), linestyle ('-'), linewidth and line color
    line1 = ax.plot_date(times, data, 'bo-', markersize=6, linewidth=2, color='#AAAAFF')
    # Make second line, if data2 has been passed in.
    # TODO:  Handle the optional second dataset better.  Maybe set the Default to None instead 
    # of an empty string
    if type(data2) != str:
        line2 = ax.plot_date(times, data2, 'rx-', markersize=6, linewidth=2, color='#FFAAAA')
        lines = []
        lines.extend(line1)
        lines.extend(line2)
        fig.legend((lines), ('model', 'obs'), loc='upper right')

    fig.savefig(myworkdir + '/' + myfilename + '.png')
