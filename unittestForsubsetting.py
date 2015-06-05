import numpy


#fakeData is a foo DS.values (t,lat,lon)
fakeData=numpy.ones((60,2,2))
#times is a foo DS.times
times = numpy.arange(60)

#put a unique number on the t-axis in the DS.values so we can 
#keep track 
for i in xrange(60):
	fakeData[i][0][0]= i+1
	
print 'fakeData ', fakeData
print 'fakeData.shape ', fakeData.shape
print 'times ', times

#DJF
month_start = 12
month_end = 2

#this stuff is basically out calc_climatology_season 
#and reshape_monthly 

offset = slice(month_start - 1, month_start - 13)
e = fakeData[offset]
ym= (e.shape[0]/12),12
ll = e.shape[1:]

b= b=tuple(ym+ ll)
month_index = slice(0, 13 - month_start + month_end)

#give fake data the shape (num_yrs, 12,lat,lon)
e.shape = b
print 'slicedData before averaging on the months', e[:,month_index].shape
slicedData = e[:,month_index].mean(axis=1)

#include here changing DS.time to reflect the slicing that occured
#this currently isn't part of the original PR, but I agree is is useful to add
b=times[offset]
newtimes=[]
for i in range(0,len(b),11):
	newtimes.append(b[i:i+(13-month_start+month_end)])

print 'fakeData.shape ', fakeData.shape
print 'times ', times
print 'newtimes ', newtimes
print 'slicedData.shape ', slicedData.shape
print 'slicedData ', slicedData