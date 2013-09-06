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

import netCDF4
import re
import pdb

#  ********************************************************************
#         CMORTable()
#
#  ********************************************************************
class CMORTable:   
    '''
    Create dictionary based on a file using key:value standard      
    '''
    def __init__( self, inpath, table, entry=None ):
        '''
        Read CMIP5 Table and convert into a dictionary
        '''
        f=open( inpath + '/' + table, 'r')

        if( f == None ):
            print "Table file %s does  not exist " % (inpath + "/" + table )

        lines = f.readlines()

        startParse=[0]
        stopParse=[len(lines)]

        # --------------------------------
        # extract user specified entry
        # -------------------------------
        if( entry != None ):
            startParse = [ i for i in range(len(lines)) \
                           if re.match( ".*entry.*"+entry+".*", lines[i] ) != None  ]
            stopParse  = [ i for i in range(startParse[0]+2, len(lines)) \
                         if re.match( ".*==========.*", lines[i] ) != None  ]
            
        self.dico = dict([ tuple(lines[i].split(":")) 
                           for i in range(startParse[0], stopParse[0])
                           if len(lines[i].split(':')) == 2 ] )

        # --------------------------------
        # extract levels
        # -------------------------------
        if 'requested' in self.dico.keys():

            self.dico['levels'] = self.dico['requested'].split('!')[0].split()
            # --------------
            # Convert to int
            # ---------------
            self.dico['levels'] = [ int( float( self.dico['levels'][i] ) )
                                    for i in range( len( self.dico['levels'] ) )]
            self.dico['levels'].sort()

    def __getitem__( self, key ):
        '''
        Get rid of end of line comments and strip new lines CR "/n"
        '''
        return self.dico[key].split("!")[0].strip()

    def __setitem__( self,key,value ):
        '''
        '''
        self.dico[key]=value

    def __delete__( self, key ):
        '''
        '''
        del self.dico[key]



#  ********************************************************************
#     Global Attributes
#
#  Manage Global Attributes in a cmor file
#  ********************************************************************
class CMORAttributes:
    '''
    Manage Global Attributes.
    '''
    def __init__( self, file ):
        '''
        Open Cmor file
        '''
        self.filename = file
        self.f = netCDF4.Dataset( self.filename, 'r+' )
        
    def GlbDel( self, attribute ):
        '''
        Delete attribute
        '''
        self.f.__delattr__(attribute)
        
    def GlbSet( self, attribute, value):
        '''
        Set attribute
        '''
        self.f.__setattr__(attribute, value)

    def VarDel( self, variable,attribute ):
        '''
        Delete Variable attribute
        '''
        var=self.f.variables[variable]
        var.__delatttr__(attribute)
        
    def VarSet( self, variable, attribute, value):
        '''
        Set Variable attribute
        '''
        var=self.variables[variable]
        var.__setattr__(attribute,value)
    def close(self):
        '''
        '''
        self.f.close()

