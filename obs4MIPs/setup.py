#!/usr/bin/env python
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

from distutils.core import setup

setup(name='obs4MIPS',
      version='1.0',
      description='Convert observation data to CMIP5s',
      author='Denis Nadeau',
      author_email='denis.nadeau@nasa.gov',
      url='http://nccs.nasa.gov',
      py_modules=['obs4MIPs_process'],
      packages=['','factory', 'Toolbox'],
      package_data={'': ['Tables/*','examples/ECMWF/Y2013/*','examples/TRMM/v7/*']},
     )
