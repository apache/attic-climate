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


import pdb
import shutil
import os,sys
from numpy import arange
from Toolbox.CMORresources import CMORAttributes

#  ********************************************************************
#         ESGFresources()
#
#  ********************************************************************
class ESGFresources:
    '''
    Create dictionary based on a file using key=value standard      
    '''
    def __init__(self,rcFile):
        '''
        Read CMIP5 Table and convert into a dictionary
        strip quote double quote, leading and trailing white space
        from key and value.
        '''
        f=open( rcFile, 'r')
        lines=f.readlines()
        f.close()

        self.resources=dict([(key.strip(), value.strip(),) 
                             for line in lines if line != '\n' \
                                 and line[0] != "#" 
                             for (key, value) in
                             [line.strip().\
                                  replace("'","").\
                                  replace("\"","").\
                                  rstrip().\
                                  split("=")]])

        for key in self.resources.keys():
            self.resources[key]=self.resources[key].replace("\\","\"")
            
        self.xcl=None
        try:
            self.xcl=self.resources['excel_file']
            rc=self.ReadXCL()
        except:
            pass

    def __getitem__(self,key):
        '''
        Retreive item from resource dictionary
        '''
        return self.resources[key]

    def __setitem__(self,key,value):
        '''
        '''
        self.resources[key]=value

    def __delete__(self,key):
        '''
        '''
        del self.resources[key]

    def ReadXCL(self):
        '''
        Read Excel Table and fill rc variable related field.
        '''
        try:
           import xlrd
        except:
           print "****** Could not find xlrd Python Package ****"
           print "****** Please install xlrd package to read excel files ****"

        if( os.path.isfile(self.xcl) ):
		wb=xlrd.open_workbook(self.xcl)
        else:
           print "****** Could not find "+self.xcl+" file ****"
           print "****** Please check excel file name ****"
           raise NameError(self.xcl)

        sheet=wb.sheet_by_name('Variables')

        self.resources['cmor_var']    = [ sheet.row( i )[ 0 ].value.\
                                          encode('ascii','ignore') \
                                          for i in arange(sheet.nrows-2) + 2 ]

        self.resources['original_var'] = [ sheet.row( i )[ 1 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2 ]

        self.resources['original_units']=[ sheet.row( i )[ 2 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2 ]

        self.resources['level']         =[ sheet.row( i )[ 3 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2]
                                    
        self.resources['equation']     =[ sheet.row( i )[ 6 ].value.\
                                           encode('ascii','ignore') \
                                           for i in arange(sheet.nrows-2) + 2 ]

        # -----------------------------------------------------------------
        # Make sure it is a string. The main program will call eval on it.
        # -----------------------------------------------------------------
        self.resources['cmor_var']       = str(self.resources['cmor_var'] )
        self.resources['original_var']   = str(self.resources['original_var'])
        self.resources['original_units'] =str(self.resources['original_units'])
        self.resources['equation']       =str(self.resources['equation'])
        self.resources['level']          =str(self.resources['level'])
        return 1


#  ********************************************************************
#      movefiles()                                                     
#
#  rename files in new obs4MIPS path
#  ********************************************************************
def movefiles(rc):  
    '''
    Change CMIP5 directory struture to obs4MIPS directory structure.
    Create new path and rename files following with new convention 
    Remove old directory tree.
    '''
    # ----------------------
    # New path for obs4MIPS
    # ----------------------
    path = rc['institute_id'      ]    + '/' + \
           rc['instrument'        ]    + '/' + \
           rc['project_id'        ]    + '/' + \
           rc['product'           ]    + '/' + \
           rc['modeling_realm'    ]    + '/' + \
           rc['cvrt_cmor_var'     ]    + '/' + \
           rc['frequency'         ]    + '/' + \
           rc['data_structure'    ]    + '/' + \
           rc['institute_id'      ]    + '/' + \
           rc['instrument'        ]    
 
   # -------------------------------------------------------------
   # For TRMM data set version_directory is set to 'false' so that
   # no version will be created in the directory
   # -------------------------------------------------------------
    try:
           rc['version_directory'] == 'false'
           pass
    except:
           path +=  '/V' + rc['processing_version'] + '/'

   # -----------------------------
   # Make sure the directory exist 
   # ------------------------------
    try:
        os.makedirs(path)
    except:
        None

    # -----------------
    # Rename all files
    # -----------------
    cmorpath = rc['project_id'  ]       + '/' + \
               rc['product'     ]       + '/' + \
               rc['institute_id']       + '/' 

    # -----------------
    # Manage attributes
    # -----------------
    for r,d,f in os.walk(cmorpath):
        for files in f:
            if files.endswith(".nc"):
                filetimestamp = files.split('_')[-1].strip(".nc")
                file = os.path.join(r,files)
                print file
                # -----------------
                # Delete attributes
                # ------------------
                Attr=CMORAttributes( file )
                DelGlbAttributes=eval(rc['DelGlbAttributes'].\
                                      replace('\\','\''))
                for attribute in DelGlbAttributes:
                    print "Deleting attribute: %s" % attribute
                    Attr.GlbDel(attribute)
                # -----------------
                # set attributes
                # ------------------
                SetGlbAttributes=eval(rc['SetGlbAttributes'].\
                                      replace('\\','\''))
                for (attribute,Value) in SetGlbAttributes:
                    print "Assigning attribute (%s,%s)" % (attribute,Value)
                    Attr.GlbSet(attribute,Value)
                Attr.close()

                source = ''
                if( rc['source_fn'] == 'SYNOPTIC' ):
                    source = rc['SYNOPTIC']+"z_"
                elif( rc['source_fn'] != '' ):
                    source = rc['source_fn'].split('_')[0] + '_'
                
                newfilename = rc['cvrt_cmor_var'     ] + '_' + \
                              rc['instrument'        ] + '-' + \
                              source                         + \
                              rc['processing_level'  ] + '_v'+ \
                              rc['processing_version'] + '_' + \
                              filetimestamp            + '.nc'
                
                newfilename = os.path.join(path,newfilename)
                # -----------
                # Move files
                # -----------
                print file
                print newfilename
                os.rename(file,newfilename)

                    
    # ----------------
    # Remove cmor path
    # ----------------
    shutil.rmtree( rc['project_id'] )
    return 0

