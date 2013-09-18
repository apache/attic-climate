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
    
    
