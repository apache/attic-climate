#
# -------------------------------------------------------------------------
# Copyright @ 2012-2013 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Other Rights Reserved.
# 
# NASA OPEN SOURCE AGREEMENT VERSION 1.3
# 
# THIS OPEN  SOURCE  AGREEMENT  ("AGREEMENT") DEFINES  THE  RIGHTS  OF USE,
# REPRODUCTION,  DISTRIBUTION,  MODIFICATION AND REDISTRIBUTION OF CERTAIN
# COMPUTER SOFTWARE ORIGINALLY RELEASED BY THE UNITED STATES GOVERNMENT AS
# REPRESENTED BY THE GOVERNMENT AGENCY LISTED BELOW ("GOVERNMENT AGENCY").
# THE UNITED STATES GOVERNMENT, AS REPRESENTED BY GOVERNMENT AGENCY, IS AN
# INTENDED  THIRD-PARTY  BENEFICIARY  OF  ALL  SUBSEQUENT DISTRIBUTIONS OR
# REDISTRIBUTIONS  OF THE  SUBJECT  SOFTWARE.  ANYONE WHO USES, REPRODUCES,
# DISTRIBUTES, MODIFIES  OR REDISTRIBUTES THE SUBJECT SOFTWARE, AS DEFINED
# HEREIN, OR ANY PART THEREOF,  IS,  BY THAT ACTION, ACCEPTING IN FULL THE
# RESPONSIBILITIES AND OBLIGATIONS CONTAINED IN THIS AGREEMENT.
# 
# Government Agency: National Aeronautics and Space Administration
# Government Agency Original Software Designation: GSC-16848-1
# Government Agency Original Software Title: Obs4MIPS.py
# 
# User Registration Requested. Please visit: http://opensource.gsfc.nasa.gov
# 
# Government Agency Point of Contact for Original Software:
# Enidia Santiago-Arce,
# SRA Assistant,
# (301) 286-8497
# -------------------------------------------------------------------------

# from: http://www.eol.ucar.edu/projects/ceop/dm/documents/refdata_report/eqns.html
from numpy import exp
import pdb

def CtoF(tf):
    return ( tc * 9. / 5. ) + 32.0

def CtoK(tc):
    return tc + 273.15

def FtoK(tf):
    return ( (tf - 32) * 5.0 / 9.0) + 273.15

def FtoC(tf):
    return (tf - 32.0) * 5.0 / 9.0

def KtoC(tk):
    return (tk - 273.15 )

def KtoF(tk):
    return ( ( tk - 273.15 ) * 9.0 / 5.0 ) + 32.0

def ComputeES(tc):
    '''
    Tc: Temperature in deg Celsius
    es: Saturation vapor pressure in mbar
    '''
    es = 6.112 * exp( ( 17.67 * tc ) / ( tc  + 243.5 ) );
        
    return es

def ComputeE(td):
    '''
    Td: dew point in deg Celcius
    e: vapor pressure in mbar
    '''
    e  = 6.112 * exp( ( 17.67 * td) / ( td + 243.5 ) );
    return e

def ComputeQ(h):
    '''
    td: in celsius
    p:  in mbar
    '''

    sp  = h.getData( variable='sp' )
    sp  = sp/100 # from Pa to Mb
    
    d2m = h.getData( variable='d2m' )
    d2m = KtoC(d2m)
    
    e = ComputeE(d2m)
    q = ( 0.622 * e ) / ( sp - ( 0.378 * e ) );
    return q


def ComputeRH( h ):
    '''
    f is the netCDF file handle containing t2m and d2m in the same file
    '''

    t2m = h.getData( variable='t2m' )
    t2m = KtoC(t2m)
    
    d2m = h.getData( variable='d2m' )
    d2m = KtoC(d2m)
    
    es  = ComputeES(t2m)
    e   = ComputeE(d2m)
    RH  = 100 * (e /es )
    return RH
    
def ComputeJRA25RH( h ):
    '''
    f is the netCDF file handle containing  and TMPprs in DEPRprs the same file
    '''
    #pdb.set_trace()
    ta = h.getData( variable='tmpprs' )
    ta = KtoC(ta)
    
    da = h.getData( variable='deprprs' )
    da = KtoC(da)
    
    es  = ComputeES(ta)
    e   = ComputeE(da)
    RH  = 100 * (e /es )
    return RH
    
    
