#!/usr/bin/env python
#
# -------------------------------------------------------------------------
# Copyright @ 2012-2013 United States Government as represented by
# the Administrator of the National Aeronautics and Space Administration.
# All Other Rights Reserved.
# 
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
# -------------------------------------------------------------------------


import cdms2
import cdtime
import cmor
import sys
import getopt
import factory
import numpy
from factory.formats import import_equation
from Toolbox.ESGFresources import *
from Toolbox.CMORresources import CMORTable


# ************************************************************************
#                              process()                               
#                                                                      
#      Convert to obs4MIPS file format.                                
# ************************************************************************
def process( rc ):
    '''
    Convert netcdf/matlab/grads files into CMIP5 format.
    '''
    #pdb.set_trace()
    # ----------------------------
    #  Loop yearly on file list.  
    # ----------------------------
    for year in rc['years'].split(","):
        if(year == ''):
            files= os.popen( "ls " + rc['file_template'] ).readlines()
        else:
            # ------------------------------------------------
            # Use string formating for path with same argument 
            # ------------------------------------------------
            try:
                tmplFile = rc['file_template'] % (year)
            except:
                tmplFile = rc['file_template'].format(year)
            if( not os.path.isfile( tmplFile) ) :
                print "**** Warning %s not found\n" % ( tmplFile )
                continue
            files= os.popen( "ls " + tmplFile).readlines()

        if( files == [] ):
            print "No file found: Check your resource file"
            return -1
        # ------------------------------------------------
        # Get the right handler to manage this file format
        # ------------------------------------------------
        Handler = factory.HandlerFormats(files[0].strip())

        # -----------------------------------
        # Take care of cmor initialization.
        # -----------------------------------
        cmor.setup(inpath=rc['inpath'],
                   netcdf_file_action = cmor.CMOR_REPLACE)
      
        cmor.dataset(experiment_id = rc['experiment_id'], 
                     institution   = rc['institution'  ],
                     calendar      = rc['calendar'     ],
                     institute_id  = rc['institute_id' ],
                     model_id      = rc['model_id'     ],
                     source        = rc['source'       ],
                     contact       = rc['contact'      ],
                     references    = rc['references'   ])
      
	
        # -----------------------------------------
        # add extra Global Attributes for obs4MIPs.
        # -----------------------------------------
        cmor.set_cur_dataset_attribute( 'instrument',     rc['instrument'    ])
        cmor.set_cur_dataset_attribute( 'mip_specs',      rc['mip_specs'     ])
        cmor.set_cur_dataset_attribute( 'data_structure', rc['data_structure'])
        cmor.set_cur_dataset_attribute( 'source_type',    rc['source_type'   ])
        cmor.set_cur_dataset_attribute( 'source_id',      rc['source_id'     ])
        cmor.set_cur_dataset_attribute( 'realm',          rc['realm'         ])
        cmor.set_cur_dataset_attribute( 'obs_project',    rc['obs_project'   ])
        cmor.set_cur_dataset_attribute( 'processing_version',
                                        rc['processing_version'] )
        cmor.set_cur_dataset_attribute( 'processing_level',
                                        rc['processing_level'] )

        cmor.load_table(rc['table'])

        # ---------------------------------------------------------------------
        # We loop on each file found, a new cmor file will be create on each
        # iteration.  If you want to aggregate, you need to use Grads ctl file
        # or NeCDF list of file.
        # ---------------------------------------------------------------------
        for file in files:
	
            fnm=file.strip()    # Get rid of \n
            aVariable  = eval(rc['original_var'])
            nbVariable = len(aVariable)

            # -----------------------------------------------------
            # ECMWF needs synoptic time 00z and 12z in he filename.
            # We extract it from the first file in the list.
            # -----------------------------------------------------
            if( rc['source_fn'] == 'SYNOPTIC' ):
                index = fnm.find('z.')
                rc['SYNOPTIC'] = fnm[index-2:index]

            # -----------------------
            # Work on all variables
            # -------------------------
            for j in arange(nbVariable):
                # ----------------------------------------------------
                # Fetch the variable directly or excute equation.
                # ----------------------------------------------------
                try:
                    variable=aVariable[j]
                    Handler.open(fnm, variable=variable)
                    rc['cvrt_original_var']   = aVariable[j]
                    print "Working on variable %s " % variable
                except:
                    if( aVariable[j] != 'equation' ) :
                        print "Variable %s can't open" % variable
                        continue
                    else:
                        print "Executing %s " % eval(rc['equation'])[j]
                
#                pdb.set_trace()
                rc['cvrt_original_units'] = eval(rc['original_units'])[j]
                rc['cvrt_cmor_var']       = eval(rc['cmor_var'])[j]
                rc['cvrt_equation']       = eval(rc['equation'])[j]
                rc['cvrt_level']          = eval(rc['level'])[j]
                
                data=Handler.getData()

                # ----------------------------------------------------------
                # Evaluate equation if needed. Usually used to change units
                # ----------------------------------------------------------
                if( rc['cvrt_equation'][0] == '@' ):
                    fncName = rc['cvrt_equation'][1:]
                    fnc = import_equation( "equations.%s" %  fncName )
                    data[:]= fnc(Handler)
                else:
                    data[:]=eval(rc['cvrt_equation'])
         
                # -------------------------------------------------------------
                # Save filled value in case data type is changed in createAxes
                # -------------------------------------------------------------
                fill_value = data.fill_value

                #  ---------------------------------------------
                #  Extract latitude/longitude
                #  ---------------------------------------------
                lonvals=Handler.getLongitude()
                latvals=Handler.getLatitude()
                # ---------------------
                # Create cmor time axis
                # ----------------------
                (rel_time, rel_time_bnds) = createTime(Handler, rc)

                # ---------------------------------------------------
                # Create cmor axes and add an axis to data if needed
                # ---------------------------------------------------
                (axes, data) = createAxes( rc, latvals, lonvals, data )
                                
                axis_ids = list()
                for axis in axes:
                    axis_id = cmor.axis(**axis)
                    axis_ids.append(axis_id)
            
                # ----------------------------------------------------------
                # Create cmor variable
                # Note: since this is in the loop, a new cmor file will be
                # create for each cmor write command.
                # ----------------------------------------------------------
                varid = cmor.variable(table_entry   = rc['cvrt_cmor_var'],
                                      axis_ids      = axis_ids,
                                      history       = '',
                                      missing_value = fill_value,
                                      original_name = rc['cvrt_original_var'],
                                      units         = rc['cvrt_original_units']
                                      )
                # -------------------------------
                # Write data for this time frame.
                # -------------------------------
                cmor.write(varid,data,\
                           time_vals=rel_time,time_bnds=rel_time_bnds)
                cmor.close(varid,file_name=True)

                # ---------------------------------------
                # Rename cmor files according to project.
                # ---------------------------------------
                if( movefiles(rc) ):
                    return -2 

        cmor.close()
    return 0



# ********************************************************************
#
#      createTime()
#
#   Define Time and Time bound axes for cmor
#
# ******************************************************************** 
def createTime(Handler, rc):
    '''
    InputtimeUnits: specified from resource file or from first file
    in a list of file.
    
    return relative time and time bounds using OutputTimeUnits from
    resource file.
    '''
    # ----------------------------------------------------
    # Retrieve time units from file if not provided in the
    # resource file.
    # ----------------------------------------------------
    InputTimeUnits = Handler.getTimeUnits(rc['InputTimeUnits'])
    
    #  --------------------------------------------------------
    #  Create time relative to January 1st 1900 to facilitate
    #  Threds software file handling.
    #  -------------------------------------------------------

    cur_time = Handler.getTime(InputTimeUnits)
    
    rel_time     =[cur_time[i].torel(rc['OutputTimeUnits']).value  
                   for i in range(len(cur_time))]
    
    if( len(rel_time) == 1 ) :
	deltarel = 1
    else:
       deltarel = rel_time[2] - rel_time[1]

    rel_time_bnds = rel_time[:]
    rel_time_bnds.append(rel_time[-1]+deltarel)
    return rel_time, rel_time_bnds

# ********************************************************************
# 
#  getCMIP5lev()
#
#  Extract CMIP5 mandatory level and recreate a new data array.
#  They are 16 mandatory levels.
# 
# ********************************************************************
def getCMIP5lev(data,rc):
    '''
    '''
    oTable               = CMORTable(rc['inpath'], rc['table'], "plevs")
    # ----------------------
    # Extract spefied levels
    # ----------------------
    if( 'levels' in oTable.dico.keys() ):
        #pdb.set_trace() 
        dataLevels = data.getLevel()[:]
        if( data.getLevel().units == "millibars" or
            data.getLevel().units == "hPa"       or
            data.getLevel().units == "mbar"    ):
            # --------------------------
            # Change units for to Pascal
            # ---------------------------
            LevelScaleFactor = 100
            dataLevels = data.getLevel()[:] * LevelScaleFactor

        # ----------------------------------------
        # No level selected, return all data array
        # ----------------------------------------
        if( len(rc['cvrt_level'].split(":")) == 1 ):
            levels =  [ float(item) for item in dataLevels ]
            lev=cdms2.createAxis( levels )
            lev.designateLevel()
            lev.units="pa"
            lev.long_name=data.getLevel().long_name
            #lev.id="lev"
            #lev=data.getAxis(1)
            #lev.__setattr__('_data_',dataLevels.astype(float))
            #lev.__setattr__('units',"Pa")
            #lev.units="hPa"
            data2=data.pressureRegrid(lev)
            return data2
        
        if( rc['cvrt_level'].split(':')[1] == "CMIP5" ):
            lev=cdms2.createAxis( [ float(item/LevelScaleFactor)
                                    for item in dataLevels
                                    if item in oTable.dico['levels' ] ] )

            lev.designateLevel()
            lev.units="pa"
            lev.long_name = data.getLevel().long_name
            data2=data.pressureRegrid(lev)
            lev[:]=lev[:]*LevelScaleFactor
            return data2
        else:
            # -----------------------
            # Assume a list of values
            # -----------------------
            levels = rc['cvrt_level'].split(':')[1].split(",")
            # --------------------------
            # Change units to Pascal
            # ---------------------------
            dataLevels = [ float(rc['cvrt_level'].split(":")[1].split(",")[i]) * \
                           LevelScaleFactor for i in range(len(levels)) ]
            # -----------------------------------
            # Match dataLevels with CMIP5 levels
            # Use file units
            # -----------------------------------
            lev=cdms2.createAxis( [ float(item/LevelScaleFactor)
                                    for item in dataLevels
                                    if item in oTable.dico['levels' ] ] )
            # -----------------------------------
            # Set axis metadata
            # -----------------------------------
            lev.units="pa"
            lev.long_name = data.getLevel().long_name
            lev.designateLevel()
            # -----------------------------------
            # Extract specified levels
            # -----------------------------------
            data2=data.pressureRegrid(lev)
            # -----------------------------------
            # Scale data back
            # -----------------------------------
            lev[:]=lev[:]*LevelScaleFactor
            return data2
            


        
    return data
# ********************************************************************
#
#      createAxes()
#
#   Define axes required by cmor and add z axis to data if needed
#
# ******************************************************************** 
def createAxes(rc, latvals, lonvals, data):
    #  ---------------------------------------------
    #  Create time/lat/lon axes using a dictionary
    #  ---------------------------------------------
    axes = [ 
        {'table_entry' : 'time',
         'units'       : rc['OutputTimeUnits']},
        
        {'table_entry' : 'latitude',
         'units'       : 'degrees_north',
         'coord_vals'  : latvals,
         'cell_bounds' : latvals.getBounds()},             
        
        {'table_entry' : 'longitude',
         'units'       : 'degrees_east',
         'coord_vals'  : lonvals,
         'cell_bounds' : lonvals.getBounds()},
        ]
    
    fill_value = data.fill_value

    if( rc['cvrt_level'] == 'height2m' ):
        axes.append({'table_entry' : 'height2m',
                     'units'       : 'm',
                     'coord_vals'  : [2.0] })
        data = numpy.array(data[:])
        data = data[:,:,:,numpy.newaxis]

    elif( rc['cvrt_level'] != '' ):
        data = getCMIP5lev( data, rc )
        levels=data.getLevel()[:]
        axes = numpy.insert(axes, 1,
                           {'table_entry' : 'plevs',
                            'units'       : 'Pa',
                            'coord_vals'  : levels })


    return axes, data

# ********************************************************************
#
#      usage()                                                          
#                                                                     
# ******************************************************************** 
def usage(message):
    '''
    Describe program synopsis.
    '''
    print
    print "*************************"
    print message
    print "*************************"
    print
    print
    print "obs4MIPS_process.py [-h] -r resource"
    print "   resource:   File containing Global attributes"
    print ""
    print "obs4MIPS will convert an input data file into CMIP5 format using "
    print "CMOR.  A directory path will be creating using CMOR by default or "
    print "using a template provided in the resource file."
    print
   
# ********************************************************************
#
#      main()                                                          
#                                                                     
# ******************************************************************** 
def main():
    '''
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hy:r:",
                                   ["help" ,"year=","resource="])
    except getopt.GetoptError, err:
        usage(str(err))# will print something like "option -a not recognized"
        return(2)

    # --------------------------
    # Verify passed arguments
    # --------------------------
    year     = -1
    resource = None
    for o, a in opts:
        if o in ("-r", "--resource"):
            resource = a
        elif o in ("-h", "--help"):
            usage()
            return(0)
        elif o in ("-y", "--year"):
            yr = a
        else:
            assert False, "unhandled option"

    # ------------------------------
    # Does the resource file exist?
    # ------------------------------
    if( resource == None ) or ( not os.path.isfile( resource ) ) :
        usage("bad Input Resource File")
        return 1

    # -----------------------
    # Read in "rc" file
    # -----------------------
    rc=ESGFresources(resource)

    # --------------------------------
    # Extract CMIP5 Table information
    # --------------------------------
    oTable               = CMORTable(rc['inpath'], rc['table'])
    if( not 'original_var' in rc.resources.keys() ):
        sys.exit(-1)
    rc['project_id']     = oTable[ 'project_id'     ]
    rc['product']        = oTable[ 'product'        ]
    rc['modeling_realm'] = oTable[ 'modeling_realm' ]
    rc['frequency']      = oTable[ 'frequency'      ]
    if( process(rc) ):
        return -1
            
    return 0

# ********************************************************************
#
#      Call main program and return exit code
#                                                                     
# ******************************************************************** 
if __name__ == '__main__':
    sys.exit(main())


