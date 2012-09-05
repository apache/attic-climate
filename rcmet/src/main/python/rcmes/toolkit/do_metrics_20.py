#!/usr/local/bin/python

def metrics_plots(numOBS,numMDL,nT,ngrdY,ngrdX,Times,obsData,mdlData,obsRgn,mdlRgn,obsList,mdlList,                         \
                  workdir,                                                                                                  \
                  mdlSelect,obsSelect,                                                                                      \
                  numSubRgn,subRgnName,rgnSelect,                                                                           \
                  obsParameterId,precipFlag,timeRegridOption,maskOption,seasonalCycleOption,metricOption,titleOption,       \
                                                                                                  plotFileNameOption):

 ##################################################################################################################
 # Routine to compute evaluation metrics and generate plots
 #    (1)  metric calculation
 #    (2) plot production
 #    Input: 
 #        numOBS           - the number of obs data. either 1 or >2 as obs ensemble is added for multi-obs cases
 #        numMDL           - the number of mdl data. either 1 or >2 as obs ensemble is added for multi-mdl cases
 #        nT               - the length of the data in the time dimension
 #        ngrdY            - the length of the data in Y dimension
 #        ngrdX            - the length of the data in the X dimension
 #        Times            - time stamps
 #        obsData          - obs data, either a single or multiple + obs_ensemble
 #        mdlData          - mdl data, either a single or multiple + obs_ensemble
 #        obsRgn           - obs time series averaged for subregions
 #        mdlRgn           - obs time series averaged for subregions
 #        obsList          - string describing the observation data files
 #        mdlList          - string describing model file names
 #        workdir 	   - string describing the directory path for storing results and plots
 #        mdlSelect        - the mdl data to be evaluated
 #        obsSelect        - the obs data to be used as the reference for evaluation
 #        numSubRgn        - the number of subregions
 #        subRgnName       - the names of subregions
 #        rgnSelect        - the region for which the area-mean time series is to be evaluated/plotted
 #        obsParameterId   - int, db parameter id. ** this is non-essential once the correct metadata use is implemented
 #	  precipFlag       - to be removed once the correct metadata use is implemented
 #        timeRegridOption - string: 'full'|'annual'|'monthly'|'daily'
 #        seasonalCycleOption - int (=1 if set) (probably should be bool longterm) 
 #	  metricOption - string: 'bias'|'mae'|'acc'|'pdf'|'patcor'|'rms'|'diff'
 #        titleOption - string describing title to use in plot graphic
 #        plotFileNameOption - string describing filename stub to use for plot graphic i.e. {stub}.png
 #    Output: image files of plots + possibly data
 ##################################################################################################################

 import sys
 import os
 import math
 import subprocess
 import datetime
 import pickle
 import numpy as np
 import numpy.ma as ma
 import Nio
 import plots
 import utils.fortranfile
 import storage.db_v12
 import storage.files_20
 import process_v12
 import metrics_v12

  #####################################################################################################
  # Select the model for calculating seasonal cycles (opt) and metrics for plotting
  # From now on, only a single model identified by mdlSelect is processed.
  # For more detailed analysis, utilize user's own code in conjunction with the data file created above
  # *** NOTE *** NOTE *** NOTE * NOTE *** NOTE *** NOTE *** NOTE *** NOTE *** NOTE ***
  # NOTE: After this block, all model- and subregion-dependence is dropped. That is, results from only
  #       one model enters the next processing step. If maskOption==1, select only one region for
  #       the next processing as well.
  # NOTE: (7/8/2012) metrics calculation currently utilizes only the first obs data. need to expand later.
  #####################################################################################################
 print 'Start calculating metrics for a single selected model/signle selected region hereafter'
 mdlList=mdlList[mdlSelect]; print 'selected model= ',mdlList
 obsList=obsList[obsSelect]; print 'selected model= ',mdlList
 if(maskOption==1):         # overwrite data arrays with the area-averaged values
   mdlData=ma.zeros(nT); obsData=ma.zeros(nT)
   mdlData[:]=mdlRgn[mdlSelect,rgnSelect,:]; obsData = obsRgn[obsSelect,rgnSelect,:]
 else:
   tmpDat=ma.zeros((nT,ngrdY,ngrdX))
   tmpDat[:,:,:]=mdlData[mdlSelect,:,:,:]
   mdlData=tmpDat
   tmpDat[:,:,:]=obsData[0,:,:,:]
   obsData=tmpDat
  # Free-up some memory by overwriting big variables
 obsStore = 0; modelStore = 0; mdlRgn = 0; obsRgn = 0
 print 'Ready to enter metrics calculations: mdlData.shape, obsData.shape ',mdlData.shape,obsData.shape

  ##################################################################################################################
  #  This replaces the Seasonal Cycle calculation in Peter's code
  #  Compute 2-D climatologies: annual cycle in terms of monthly and seasonal climatology; annual climatology
  #    Introduce new vars to store climatology:
  #      monCLobs(12,ngrdY,ngrdX), seaCLobs(4,ngrdY,ngrdX), annCLobs(ngrdY,ngrdX
  #      monCLmdl(numMDL,12,ngrdY,ngrdX), seaCLmon(numMDL,4,ngrdY,ngrdX), annCLmdl(numMDL,ngrdY,ngrdX)
  #  Note: obsData and mdlData still contains the time series data prepared above.
  #  The obs/model data for each case are prepared in the matching shapes in the processings up to this point.
  #   --> If not, there is a problem.
  ##################################################################################################################
 if seasonalCycleOption==1:
   print 'Calculate the monthly and seasonal climatology: mdlData.shape, obsData.shape ',mdlData.shape,obsData.shape
   if maskOption != 1:           # 2-D climatology at the entire model grid
     print'For 2-d model domain'
     monCLobs = rcmes.metrics_v12.calc_clim_month(obsData,Times)                    # compute the seasonal means
     seaCLobs=ma.zeros((4,ngrdY,ngrdX))
     seaCLobs[0,:,:]=(monCLobs[0,:,:]+monCLobs[1,:,:]+monCLobs[11,:,:])/3.       # winter (DJF)
     seaCLobs[1,:,:]=(monCLobs[2,:,:]+monCLobs[3,:,:]+monCLobs[4,:,:])/3.        # spring (MAM)
     seaCLobs[2,:,:]=(monCLobs[5,:,:]+monCLobs[6,:,:]+monCLobs[7,:,:])/3.        # Summer (JJA)
     seaCLobs[3,:,:]=(monCLobs[8,:,:]+monCLobs[9,:,:]+monCLobs[10,:,:])/3.       # Fall   (SON)
     monCLmdl = rcmes.metrics_v12.calc_clim_month(mdlData,Times)
     seaCLmdl=ma.zeros((4,ngrdY,ngrdX))
     seaCLmdl[0,:,:]=(monCLmdl[0,:,:]+monCLmdl[1,:,:]+monCLmdl[11,:,:])/3.       # winter (DJF)
     seaCLmdl[1,:,:]=(monCLmdl[2,:,:]+monCLmdl[3,:,:]+monCLmdl[4,:,:])/3.        # spring (MAM)
     seaCLmdl[2,:,:]=(monCLmdl[5,:,:]+monCLmdl[6,:,:]+monCLmdl[7,:,:])/3.        # Summer (JJA)
     seaCLmdl[3,:,:]=(monCLmdl[8,:,:]+monCLmdl[9,:,:]+monCLmdl[10,:,:])/3.       # Fall   (SON)
   else:
     print 'For the subregion: ',rgnSelect
     tmpDat=ma.zeros(nT)
     monCLobs=ma.zeros(12); seaCLobs=ma.zeros(4); monCLmdl=ma.zeros(12); seaCLmdl=ma.zeros(4)
     tmpDat[:]=obsData[:]
     monCLobs[:]=rcmes.metrics_v12.calc_clim_month(tmpDat,Times)
     seaCLobs[0]=(monCLobs[0]+monCLobs[1]+monCLobs[11])/3.       # winter (DJF)
     seaCLobs[1]=(monCLobs[2]+monCLobs[3]+monCLobs[4])/3.        # spring (MAM)
     seaCLobs[2]=(monCLobs[5]+monCLobs[6]+monCLobs[7])/3.        # Summer (JJA)
     seaCLobs[3]=(monCLobs[8]+monCLobs[9]+monCLobs[10])/3.       # Fall   (SON)
     tmpDat[:]=mdlData[:]
     monCLmdl[:]=rcmes.metrics_v12.calc_clim_month(tmpDat,Times)
     seaCLmdl[0]=(monCLmdl[0]+monCLmdl[1]+monCLmdl[11])/3.       # winter (DJF)
     seaCLmdl[1]=(monCLmdl[2]+monCLmdl[3]+monCLmdl[4])/3.        # spring (MAM)
     seaCLmdl[2]=(monCLmdl[5]+monCLmdl[6]+monCLmdl[7])/3.        # Summer (JJA)
     seaCLmdl[3]=(monCLmdl[8]+monCLmdl[9]+monCLmdl[10])/3.       # Fall   (SON)
 print 'after monthly climatology: mdlData.shape, obsData.shape, monCLobs.shape, monCLmdl.shape ',mdlData.shape,obsData.shape,monCLobs.shape,monCLmdl.shape
 
  ##################################################################################################################
  # Part 7: metric calculation
  #      Calculate performance metrics comparing obsData and mdlData.
  #      All output is stored in metricData regardless of what metric was calculated.
  #      NB. the dimensions of metricData will vary depending on the dimensions of the incoming data
  #          *and* on the type of metric being calculated.
  #      e.g.    bias between incoming 1D model and 1D obs data (after area-averaging) will be a single number. 
  #              bias between incoming 3D model and 3D obs data will be 2D, i.e. a map of mean bias.
  #              correlation coefficient between incoming 3D model and 3D obs data will be 1D time series.
  # JK:
  #    For now, the metrics
  #     (1) over the entire domain are calculated for annaul mean climatology (i.e., means for the entire period)
  #     (2) over subregions will be calculated for monthly mean climatology (i.e., annual cycle in each subregion)
  ##################################################################################################################
 #print 'before metrics calculation: mdlData.shape, obsData.shape ',mdlData.shape,obsData.shape
 print '(Part 7): metric option= ',metricOption
  # create a temporary array to store model data according to the:
   ## record lenth (nT), the number of models (numMDL) option(mdlSelect) and area-averaging option (maskOption)
 if(maskOption!=1):                              # metrics at every grid points within the full domain --> results in 2-D contour plots
   tmpMDL=ma.zeros((nT,ngrdY,ngrdX)); metricData=ma.zeros((ngrdY,ngrdX))
 else:                                           # only plot annual cycle in terms of monthly means at this time. Seasonal will be added
   tmpMDL=ma.zeros(12); metricData=ma.zeros(12)
 if metricOption=='bias':
   metricTitle = 'Bias'; optn='mean'
   if(maskOption!=1):                            # Metrics at each grid point over the entire domain
     metricData = rcmes.metrics_v12.calc_bias_annual(mdlData,obsData,optn)
   else:
     metricData = monCLmdl - monCLobs
 if metricOption=='mae':
   metricTitle = 'Mean Absolute Error'; optn='abs'
   if(maskOption!=1):                            # Metrics at each grid point over the entire domain
     if(mdlSelect>=0):
       metricData = rcmes.metrics_v12.calc_bias_annual(mdlData,obsData,optn)
     if(mdlSelect<0):
       n=0
       while n<numMDL:
         tmpMDL=mdlData[n,:,:,:]
         metricData[n,:,:] = rcmes.metrics_v12.calc_bias_annual(tmpMDL,obsData,optn)
         n+=1
   if(maskOption==1):     # TBW
     pass
 if metricOption=='rms':
   metricTitle = 'RMS Error'
   if(maskOption!=1):                            # Metrics at each grid point over the entire domain
     if(mdlSelect>=0):
       metricData = rcmes.metrics_v12.calc_rms_annual(mdlData,obsData)
     if(mdlSelect<0):
       n=0
       while n<numMDL:
         tmpMDL=mdlData[n,:,:,:]
         metricData[n,:,:] = rcmes.metrics_v12.calc_rms_annual(tmpMDL,obsData)
         n+=1 
   if(maskOption==1):     # TBW
     pass
 if metricOption=='difference':
   metricData = rcmes.metrics.calc_difference(mdlData,obsData)
   metricTitle = 'Difference'
 if metricOption=='patcor':
   metricTitle = 'Pattern Correlation'
   if(maskOption!=1):                            # Metrics at each grid point over the entire domain
     if(mdlSelect>=0):
       metricData = rcmes.metrics.calc_pat_cor2D(mdlData,obsData,nT)
     if(mdlSelect<0):
       n=0
       while n<numMDL:
         tmpMDL=mdlData[n,:,:,:]
         metricData = rcmes.metrics.calc_pat_cor2D(tmpMDL,obsData,nT)
         n+=1
   if(maskOption==1):     # TBW
     pass
 if metricOption=='acc':
   metricTitle = 'Anomaly Correlation'
   metricData = rcmes.metrics.calc_anom_cor(mdlData,obsData)

 #return -1         # no plot production

  ##################################################################################################################
  # Part 8: Plot production
  #      Produce plots of metrics and obs,model data.
  #      Type of plot produced depends on dimensions of incoming data.
  #              e.g. 1D data is plotted as a time series.
  #                   2D data is plotted as a map.
  #                   3D data is plotted as a sequence of maps.
  ##################################################################################################################

  # delete old (un-saved) plot files
 fileName=workdir+'/pr_both'+ '.png'
 if(os.path.exists(fileName)==True):
   cmnd='rm -f ' + fileName
   subprocess.call(cmnd,shell=True)
 fileName=workdir+'/pr_'+ '.png'
 if(os.path.exists(fileName)==True):
   cmnd='rm -f ' + fileName
   subprocess.call(cmnd,shell=True)

  # Data-specific plot options: i.e. adjust model data units & set plot color bars
 colorbar = 'rainbow'
 if precipFlag==True:
    colorbar = 'precip2_17lev'              # set color bar for prcp
 if obsParameterId==31: colorbar = 'gsdtol' # set color bar for MODIS cloud data

  # 1. dimensional data, e.g. Time series plots
 if metricData.ndim==1:
   print 'Producing time series plots'
   year_labels = True
   mytitle = 'Area-mean '
    # If producing seasonal cycle plots, don't want to put year labels on the time series plots.
   #print 'seasonalCycleOption= ',seasonalCycleOption
   if seasonalCycleOption==1:
     year_labels = False
     mytitle = 'Annual cycle over the ' + subRgnName[rgnSelect] + 'region'; print 'mytitle = ',mytitle
     # Create a list of datetimes to represent the annual cycle, one per month.
     times = []
     for m in xrange(12):
       times.append(datetime.datetime(2000,m+1,1,0,0,0,0))
    # Special case for pattern correlation plots. TODO: think of a cleaner way of doing this.
    # Only produce these plots if the metric is NOT pattern correlation.
   if (metricOption!='patcor')&(metricOption!='acc'):  # for anomaly and pattern correlation, can't plot time series of model, obs as these are 3d fields
                               # TODO: think of a cleaner way of dealing with this. Produce the time series plots with two lines: obs and model
     #print 'times = ',times; print monCLmdl.shape,len(times)
     status = rcmes.plots.draw_time_series_plot(monCLmdl,times,plotFileNameOption+'both',workdir,data2=monCLobs,mytitle=mytitle,ytitle='Y',xtitle='time',year_labels=year_labels)
    # Produce the metric time series plot (one line only)
   mytitle = titleOption
   if titleOption=='default':
        mytitle = metricTitle+' model v obs'
   status = rcmes.plots.draw_time_series_plot(metricData,times,plotFileNameOption,workdir,mytitle=mytitle,ytitle='Y',xtitle='time',year_labels=year_labels)

  # 2. dimensional data, e.g. Maps
 if metricData.ndim==2:
    # Calculate color bar ranges for data such that same range is used in obs and model plots
    # for like-with-like comparison.
   mymax = max(obsData.mean(axis=0).max(),mdlData.mean(axis=0).max())
   mymin = min(obsData.mean(axis=0).min(),mdlData.mean(axis=0).min())
    # Time title labels need their format adjusting depending on the temporal regridding used,
    #          e.g. if data are averaged to monthly,
    #               then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'
    #  Also, if doing seasonal cycle compositing 
    #  then want to write 'Jan','Feb','Mar' instead of 'Jan 2002','Feb 2002','Mar 2002' etc 
    #  as data are representative of all Jans, all Febs etc. 
   if(timeRegridOption=='daily'):
       timeFormat = "%b %d, %Y"
   if(timeRegridOption=='monthly'):
       timeFormat = "%b %Y"
   if(timeRegridOption=='annual'):
       timeFormat = "%Y"
   if(timeRegridOption=='full'):
       timeFormat = "%b %d, %Y"
    # Special case: when plotting bias data, we also like to plot the mean obs and mean model data.
    #               In this case, we need to calculate new time mean values for both obs and model.
    #               When doing this time averaging, we also need to deal with missing data appropriately.
    #
    # Classify missing data resulting from multiple times (using threshold data requirment)
    #   i.e. if the working time unit is monthly data, and we are dealing with multiple months of data
    #        then when we show mean of several months, we need to decide what threshold of missing data we tolerate
    #        before classifying a data point as missing data.
    # Calculate time means of model and obs data
   print 'Plotting: mdlData.shape, obsData.shape ',mdlData.shape,obsData.shape
   mdlDataMean = mdlData.mean(axis=0)
   obsDataMean = obsData.mean(axis=0)
   print 'Plotting: shapes of mdlDataMean/obsDataMean ',mdlDataMean.shape,obsDataMean.shape
   #return -1
    # Calculate missing data masks using tolerance threshold of missing data going into calculations
   obsDataMask = rcmes.process.create_mask_using_threshold(obsData,threshold=0.75)
   mdlDataMask = rcmes.process.create_mask_using_threshold(mdlData,threshold=0.75)
    # Combine data and masks into masked arrays suitable for plotting.
   mdlDataMean = ma.masked_array(mdlDataMean, mdlDataMask)
   obsDataMean = ma.masked_array(obsDataMean, obsDataMask)
    # Plot model data
   mytitle = 'Model data: mean between '+Times[0].strftime(timeFormat)+' and '+Times[-1].strftime(timeFormat)
   status = rcmes.plots.draw_map_color_filled(mdlDataMean,lats,lons,plotFileNameOption+'model',workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)
    # Plot obs data
   mytitle = 'Obs data: mean between '+Times[0].strftime(timeFormat)+' and '+Times[-1].strftime(timeFormat)
   status = rcmes.plots.draw_map_color_filled(obsDataMean,lats,lons,plotFileNameOption+'obs',workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)
    # Plot metric
   mymax = metricData.max()
   mymin = metricData.min()
   mytitle = titleOption
   if titleOption=='default':
     mytitle = metricTitle+' model v obs '+Times[0].strftime(timeFormat)+' to '+Times[-1].strftime(timeFormat)
   status = rcmes.plots.draw_map_color_filled(metricData,lats,lons,plotFileNameOption,workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,diff=True,niceValues=True,nsteps=24)

 # 3. dimensional data, e.g. sequence of maps
 if metricData.ndim==3:
   print 'Generating series of map plots, each for a different time.'
   #for t in np.arange(obsData.shape[0]):
   for t in np.arange(numMDL):
      # Calculate color bar ranges for data such that same range is used in obs and model plots
      # for like-with-like comparison.
     mymax = max(obsData[t,:,:].max(),mdlData[t,:,:].max())
     mymin = min(obsData[t,:,:].min(),mdlData[t,:,:].min())
      # Time title labels need their format adjusting depending on the temporal regridding used,
      #          e.g. if data are averaged to monthly,
      #               then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'
      #  Also, if doing seasonal cycle compositing 
      #  then want to write 'Jan','Feb','Mar' instead of 'Jan 2002','Feb 2002','Mar 2002' etc 
      #  as data are representative of all Jans, all Febs etc. 
     if(timeRegridOption=='daily'):
       timeTitle = Times[t].strftime("%b %d, %Y")
       if seasonalCycleOption==1:
          timeTitle = Times[t].strftime("%b %d (all years)")
     if(timeRegridOption=='monthly'):
       timeTitle = Times[t].strftime("%b %Y")
       if seasonalCycleOption==1:
          timeTitle = Times[t].strftime("%b (all years)")
     if(timeRegridOption=='annual'):
       timeTitle = Times[t].strftime("%Y")
     if(timeRegridOption=='full'):
       time1 = min(min(Times),min(Times))
       time2 = max(max(Times),max(Times))
       timeTitle = time1.strftime("%b %d, %Y")+' to '+time2.strftime("%b %d, %Y")
      # Plot model data
     mytitle = 'Model data: mean '+timeTitle
     status = rcmes.plots.draw_map_color_filled(mdlData[t,:,:],lats,lons,plotFileNameOption+'model'+str(t),workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)
      # Plot obs data
     mytitle = 'Obs data: mean '+timeTitle
     status = rcmes.plots.draw_map_color_filled(obsData[t,:,:],lats,lons,plotFileNameOption+'obs'+str(t),workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)
      # Plot metric
     mytitle = titleOption
     if titleOption=='default':
        mytitle = metricTitle +' model v obs : '+timeTitle
     mymax = metricData.max()
     mymin = metricData.min()
     status = rcmes.plots.draw_map_color_filled(metricData[t,:,:],lats,lons,plotFileNameOption+str(t),workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,diff=True, niceValues=True, nsteps=24)

  # Processing complete
 print 'RCMES processing completed.'

