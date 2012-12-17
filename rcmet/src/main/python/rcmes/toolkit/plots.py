"""Module that handles the generation of data plots"""


# Import Statements

from math import floor, log
import matplotlib
import Ngl 
import numpy as np
import pylab


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


def draw_cntr_map_single(pVar, lon, lat, mnLvl, mxLvl, pTitle, pName, cMap, wksType):
    """
        File:
          cn05p.py
        Synopsis:
          Draws an animation of global surface temperature over a map.
        Category:
          Contours over maps
        Author:
          Mary Haley (based on example of Tim Scheitlin)
        Date of initial publication:    
          November, 2005
        Description:
          This example draws an animation of filled contours over a map 
          showing surface temperatures (if "Animate" is set to True).
          Instead of calling Ngl.contour_map for every time step,
          Ngl.set_values is used to change the data and title after the
          initial time step.
       Effects illustrated
          o  Reading data from a netCDF file.
          o  Creating a color map using RGB triplets.
          o  Drawing color filled contours over a map.
          o  Using Ngl.set_values to change the data for the animation.
          o  Using a resource list to set many resources, for example to:
               + set color map
               + set contour levels
               + set fill colors
               + turn off contour lines and line labels
               + set some labelbar, title,  and tickmark resources
       Input:
          pVar   : the field to be plotted (2d)
          lon    : longitude (1-d)
          lat    : latitude  (1-d)
          mnLvl  : the minimum countour level
          mxLvl  : the maximum countour level
          spLvl  : label spacing
          pTitle : plot title
          pName  : name of the plot file
          cMap   : color map
          wksType: workstation type (character)
       Output:
          If "Animate" is set to True, then an animation of 31 frames
          (one per day on January) is produced. Otherwise, just one frame
          is produced.
    """

    # Open workstation
    wres = Ngl.Resources()
    wres.wkColorMap = cMap
    # plot size setup for the pdf file option
    if wksType == 'pdf':
        wres.wkPaperSize = "A4"

    # assign resolution for png option (defaule = 1024x1024)
    if wksType == 'png':
        res.wkWidth = 1000
        res.wkHeight = 1000

    wks = Ngl.open_wks(wksType, pName, wres)

    # Set up variable to hold the various plot
    # resources we want to set.
    res = Ngl.Resources()
    # Set some scalar field resources.
    res.sfXArray = lon
    res.sfYArray = lat
    # Define map lat,lon limits
    res.mpLimitMode = "LatLon"    # Limit the map view.
    res.mpMinLonF = float(lon.min())
    res.mpMaxLonF = float(lon.max())
    res.mpMinLatF = float(lat.min())
    res.mpMaxLatF = float(lat.max())
    res.mpPerimOn = True        # Turn on map perimeter.
    # Set some contour resources
    res.cnFillOn = True
    res.cnLinesOn = False             # draw (True) or not (False) contour lines
    res.cnLineLabelsOn = False             # control the writing of contour labels
    nsteps = 24
    mnLvl, mxLvl, nsteps = calc_nice_color_bar_values(mnLvl, mxLvl, nsteps)
    spLvl = (mxLvl - mnLvl) / nsteps
    res.cnLevelSelectionMode = "ExplicitLevels" # Define own levels. valid values are "ManualLevels", "AutomaticLevels"
    res.cnMinLevelValF = mnLvl
    res.cnMaxLevelValF = mxLvl
    res.cnLevels = np.arange(mnLvl, mxLvl, spLvl)
    # Set some labelbar resources.
    res.lbLabelsOn = True         # write or not the color-bar labels
    res.lbBoxLinesOn = True
    res.lbLabelStride = 2            # control the interval at which color-bar label is written (defult = 1)
    res.lbLabelFont = "default"
    res.lbLabelFontQuality = "High"
    res.lbLabelFontHeightF = .015    # Label font height. Default = .02
    res.lbLabelFontThicknessF = 2.   # default = 1.
    res.lbOrientation = "Vertical"   # or "Horizontal"
    res.lbBottomMarginF = 0.1        # default = 0.05
    res.lbTopMarginF = 0.1        # default = 0.05
    # Set a map resource.
    res.mpGridAndLimbOn = False
    res.mpGeophysicalLineColor = "Black"
    # Set some title resources.
    res.tiMainString = pTitle
    res.tiMainFontHeightF = 0.02
    # If 1d lat,lon array then assumed to be regular lat,lon grid
    if len(lat.shape) == 1:
        res.sfXCStartV = float(lon.min())
        res.sfXCEndV = float(lon.max())
        res.sfYCStartV = float(lat.min())
        res.sfYCEndV = float(lat.max())

    # Clean up
    Ngl.destroy(wks)
    del res
    del wks


def draw_map_color_filled(data, lats, lons, filename, workdir, mytitle='', rangeMax='not set', rangeMin='not set', diff=False, nsteps=20, colorTable='rainbow', niceValues=False):
    '''
     Function to draw a color filled contour map using the masked array data
     
     Input:: 
         data  -a masked numpy array of data masked by missing values
         lats,lons  -1d numpy arrays of unique latitudes and longitudes of grid points
         filename  -stub of png file created e.g. 'myfile' -> myfile.png
         workdir - directory to save images in
         mytitle - chart title
         rangeMax - (optional) max range for color bar (including for difference plots)
         rangeMin - (optional) min range for color bar
         diff    - boolean flag to say if this is a difference plot or not
     	 (if true then uses different color scale and ranges)
         nsteps  - (optional) number of color bar intervals
    	 colorTable - (optional) name of PyNGL color table
         niceValues - (optional) use nice round values for color bar labels
    
     Output::
    	 no data returned from function
         Image file produced with name {filename}.png
    '''

    # set optional argument if not set by user
    if(rangeMax == 'not set'):
        rangeMax = data.max()

    if(rangeMin == 'not set'):
        rangeMin = data.min()
 
    # For difference plots, we want color bar showing zero=white, positive=red, negative=blue
    #  so set range centred about zero
    if np.logical_and((diff == True), rangeMax == 'not set'):
        absmax = np.abs(data).max()
        rangeMin = -absmax
        rangeMax = absmax

    # Sometimes doing a difference plot, the plot becomes saturated by a few very high values
    # In this case, you can specify the maximum range using rangeMax optional argument
    if np.logical_and((diff == True), (rangeMax != 'not set')):
        absmax = rangeMax
        rangeMin = -absmax
        rangeMax = absmax

    print 'Making map plot with color filled contours'

    # Map plot
    #wks_type = 'png'
    wks_type = 'ps'
    res = Ngl.Resources()
    res.wkWidth = 1000
    res.wkHeight = 1000
    res.wkColorMap = colorTable	 

    if(diff == True):
        res.wkColorMap = "BlueDarkRed18"

    wks = Ngl.open_wks(wks_type, filename, res)
    
    resources = Ngl.Resources()

    resources.nglMaximize = True  # didn't seem to have any effect
    resources.vpWidthF = 0.8    resources.vpHeightF = resources.vpWidthF / 2.5

    # Define data lat,lon limits
    resources.cnFillOn = True     # Turn on contour fill.
    # If 2d lat,lon arrays then may not be regular lat,lon grid
    if len(lats.shape) > 1:
        resources.sfXArray = lons  # Portion of map on which to overlay
        resources.sfYArray = lats  # contour plot.

    # If 1d lat,lon array then assumed to be regular lat,lon grid
    if len(lats.shape) == 1:
        resources.sfXCStartV = float(lons.min())
        resources.sfXCEndV = float(lons.max())
        resources.sfYCStartV = float(lats.min())
        resources.sfYCEndV = float(lats.max())

    # Define map lat,lon limits
    resources.mpLimitMode = "LatLon"    # Limit the map view.

    resources.mpMinLonF = float(lons.min())
    resources.mpMaxLonF = float(lons.max())
    resources.mpMinLatF = float(lats.min())
    resources.mpMaxLatF = float(lats.max())

    resources.mpPerimOn = True        # Turn on map perimeter.

    resources.tiMainString = "~F22~" + mytitle
    resources.tiMainFontHeightF = 0.01
 
    resources.cnLineLabelsOn = False   # Turn off contour line lables
    resources.cnLinesOn = False  # Turn off contour lines (only use color filled)

    # Set up the contour levels
    if(niceValues):
        rangeMin, rangeMax, nsteps = calc_nice_color_bar_values(rangeMin, rangeMax, nsteps)


    resources.cnLevelSelectionMode = "ExplicitLevels" # Define own levels.
    resources.cnLevels = np.arange(rangeMin, rangeMax, (rangeMax - rangeMin) / nsteps)

    plot = Ngl.contour_map(wks, data, resources)

    # Clean up
    Ngl.destroy(wks) 
    del plot 
    del resources
    del wks


def draw_time_series_plot(data, times, myfilename, myworkdir, data2='', mytitle='', ytitle='Y', xtitle='time', year_labels=True):
    '''
     Function to draw a time series plot
     
     Input:: 
         data   -a masked numpy array of data masked by missing values		
         times  -a list of python datetime objects
         myfilename  -stub of png file created e.g. 'myfile' -> myfile.png
         myworkdir - directory to save images in
         data2 - (optional) second data line to plot assumes same time values)
         mytitle - (optional) chart title
    	 xtitle - (optional) y-axis title
    	 ytitle - (optional) y-axis title
    
     Output:
         no data returned from function
         Image file produced with name {filename}.png
    '''
    print 'Producing time series plot'

    fig = pylab.figure()
    ax = fig.gca()

    if year_labels == False:
        xfmt = matplotlib.dates.DateFormatter('%b')
        ax.xaxis.set_major_formatter(xfmt)

    # x-axis title
    pylab.xlabel(xtitle)

    # y-axis title
    pylab.ylabel(ytitle)

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
    pylab.ylim((ymin, ymax))

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

def draw_time_series_plot_old(data, times, myfilename, myworkdir, mytitle='', ytitle='Y', xtitle='time'):
    '''
     **DEPRECATED: This old version used PyNGL which couldn't handle dates.**
     
     New improved version (draw_time_series_plot) uses matplotlib which handles dates well.  
     
     Function to draw a time series plot
     
     Input:: 
        data   -a masked numpy array of data masked by missing values
        NB. for multiple lines use a list of arrays

        times  -a list of python datetime objects
        myfilename  -stub of png file created e.g. 'myfile' -> myfile.png
        myworkdir - directory to save images in
        mytitle - (optional) chart title
        xtitle - (optional) y-axis title
        ytitle - (optional) y-axis title

     Output::
         No data returned from function
         Image file produced with name {filename}.png
    '''

    wks_type = "png"
    wks = Ngl.open_wks(wks_type, myworkdir + '/' + myfilename)  # Open a workstation.
    t = np.arange(len(times))

    #  Set resources for titling.
    resources = Ngl.Resources()

    resources.tiMainFont = "Helvetica" # Font for title
    resources.tiXAxisFont = "Helvetica" # Font for X axis label
    resources.tiYAxisFont = "Helvetica" # Font for Y axis label
    resources.tiMainString = mytitle
    resources.tiXAxisString = xtitle
    resources.tiYAxisString = ytitle
   
    resources.xyLineThicknesses = [2.]    # Define line thicknesses

    resources.xyMarkLineModes = ["MarkLines"]
    resources.xyMarkers = [1]         # (none, dot, asterisk)
    resources.xyMarkerSizeF = 0.02        # Marker size (default
                                            # is 0.01)
                                            # (1.0 is the default).

    # Special handling dependent on if data is for a single line, 
    #  or a multiple dimensions for mulitple lines
    if len(data.shape) == 1:
        resources.xyLineColors = [189]  # Define line colors.
        resources.xyMarkerColor = [189]

    if len(data.shape) > 1:
        resources.xyLineColors = [189, 210]  # Define line colors.
        resources.xyMarkerColor = [189, 210]

    plot = Ngl.xy(wks, t, data, resources)   # Draw an XY plot.

    # Clean up.
    Ngl.destroy(wks) 
    del plot 
    del resources
    del wks
