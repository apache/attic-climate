#!/usr/local/bin/python

def decodeTimeFromString(time_string):
    '''
    # Decodes string into a python datetime object
    # Method: tries a bunch of different time format possibilities and hopefully one of them will hit.
    # 
    #   Input:  time_string - a string that represents a date/time
    #   Output: mytime - a python datetime object
    #
    #   Peter Lean   February 2011
    '''
    import time
    import datetime

    try:
        mytime = time.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y/%m/%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y%m%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y:%m:%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y%m%d%H%M%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y-%m-%d %H:%M')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass


    print 'Error decoding time string: string does not match a predefined time format'
    return 0



def decode_model_times(filelist,timeVarName):
   '''
   #  Routine to convert from model times ('hours since 1900...', 'days since ...') 
   #  into a python datetime structure
   #
   #  Input:
   #      filelist - list of model files
   #      timeVarName - name of the time variable in the model files
   #
   #  Output:
   #      times  - list of python datetime objects describing model data times
   #
   #
   #     Peter Lean February 2011
   #
   '''
   import datetime
   import re
   import string
   import math
   import numpy
   import Nio

   f = Nio.open_file(filelist[0])
   xtimes = f.variables[timeVarName]
   timeFormat = xtimes.units

   # search to check if 'since' appears in units
   try:
     sinceLoc = re.search('since',timeFormat).end()

   except:
     print 'Error decoding model times: time variable attributes do not contain "since"'
     return 0

   # search for 'seconds','minutes','hours', 'days', 'months', 'years' so know units
   units = ''
   try:
     mysearch = re.search('minutes',timeFormat).end()
     units = 'minutes'
   except:
     pass
   try:
     mysearch = re.search('hours',timeFormat).end()
     units = 'hours'
   except:
     pass
   try:
     mysearch = re.search('days',timeFormat).end()
     units = 'days'
   except:
     pass
   try:
     mysearch = re.search('months',timeFormat).end()
     units = 'months'
   except:
     pass
   try:
     mysearch = re.search('years',timeFormat).end()
     units = 'years'
   except:
     pass
   
   # cut out base time (the bit following 'since')
   base_time_string = string.lstrip(timeFormat[sinceLoc:])

   # decode base time
   base_time = decodeTimeFromString(base_time_string)


   times=[]
   for xtime in xtimes[:]:
      if(units=='minutes'):  
         dt = datetime.timedelta(minutes=xtime)
         new_time = base_time + dt

      if(units=='hours'):  
         dt = datetime.timedelta(hours=xtime)
         new_time = base_time + dt

      if(units=='days'):  
         dt = datetime.timedelta(days=xtime)
         new_time = base_time + dt

      if(units=='months'):   # NB. adding months in python is complicated as month length varies and hence ambigous.
         # Perform date arithmatic manually
         #  Assumption: the base_date will usually be the first of the month
         #              NB. this method will fail if the base time is on the 29th or higher day of month
         #                      -as can't have, e.g. Feb 31st.
         new_month = base_time.month + xtime % 12
         new_year = int(math.floor(base_time.year + xtime / 12.))
         new_time = datetime.datetime(new_year,new_month,base_time.day,base_time.hour,base_time.second,0)

      if(units=='years'):
         dt = datetime.timedelta(years=xtime)
         new_time = base_time + dt
         
      times.append(new_time)

   return times


''' NOT USED BY BOTTLE WS CALLS
import sys
import datetime 
filename = [sys.argv[1]]
time_var_name = sys.argv[2]

print filename, type(filename)
print time_var_name

times = decode_model_times(filename,time_var_name)

for time in times:
  print time.strftime('%Y-%m-%d %H:%M:%S')
'''
