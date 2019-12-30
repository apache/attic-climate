
# load required modules
import numpy as np
from cdo import *
cdo = Cdo()

############################ generate temporary netcdf files to disk - required for index calculations

def calc_nday(file):
   # number of days per year in file
   tmp = cdo.ndate(input='-selyear,2000 '+file)
   tmp = str(tmp[0])
   return(tmp)

def calc_nyear(file):
   # number of years in file
   tmp = cdo.nyear(input=file)
   tmp = str(tmp[0])
   return(tmp)

def gen_pre_basefiles(pre_file, bp_start, bp_end):
   # function to compute based period files need for pre-based indices
   # writes straight to netcdf files
   bp_start=str(bp_start)
   bp_end=str(bp_end)
   cdo.yearsum(input=pre_file, output='prcptot.nc', options='-L')
   cdo.setrtomiss('0,0.999',input='-selyear,'+bp_start+'/'+bp_end + ' '+ pre_file, output='bp_pre.nc', options='-L')   
   cdo.timpctl('95 ',input='bp_pre.nc -timmin bp_pre.nc -timmax bp_pre.nc', output='r95p_file.nc', options='-L')
   cdo.timpctl('99 ',input='bp_pre.nc -timmin bp_pre.nc -timmax bp_pre.nc', output='r99p_file.nc', options='-L')
   return;


######################################## simple threshold/block maxima indices


def run_cdd(pre_file, v_name, base_name, opt):
   # computes consecutive dry days from daily precip file
   if opt==0:
      print("writing cdd.nc .....")
      cdo.yearmax(input='-consects -lec,1 '+ pre_file, output=base_name+'_'+'cdd.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearmax(input='-consects -lec,1 '+ pre_file, returnArray=v_name))
      return(tmp)

def run_cwd(pre_file, v_name, base_name, opt):
   # computes consecutive wet days from daily precip file
   if opt==0:
      print("writing cwd.nc .....")
      cdo.yearmax(input='-consects -gtc,1 '+ pre_file, output=base_name+'_'+'cwd.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearmax(input='-consects -gtc,1 '+ pre_file, returnArray=v_name))
      return(tmp)

def run_pd(pre_file, v_name, base_name, opt):
   # computes precipiations days (>1mm) from daily precip file
   if opt==0:
      print("writing pd.nc .....")
      cdo.yearsum(input='-gtc,1 '+pre_file, output=base_name+'_'+'pd.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearsum(input='-gtc,1 '+pre_file, returnArray=v_name))
      return(tmp)

def run_r10mm(pre_file, v_name, base_name, opt):
   # computes precipiations days (>10mm) from daily precip file
   if opt==0:
      print("writing r10mm.nc .....")
      cdo.yearsum(input='-gtc,10 '+pre_file, output=base_name+'_'+'r10mm.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearsum(input='-gtc,10 '+pre_file, returnArray=v_name))
      return(tmp)

def run_r20mm(pre_file, v_name, base_name, opt):
   # computes precipiations days (>20mm) from daily precip file
   if opt==0:
      print("writing r20mm.nc .....")
      cdo.yearsum(input='-gtc,20 '+pre_file, output=base_name+'_'+'r20mm.nc', options='-L')
      return; 
   else:
      tmp = np.squeeze(cdo.yearsum(input='-gtc,20 '+pre_file, returnArray=v_name))
      return(tmp)

def run_rx1day(pre_file, v_name, base_name, opt):
   # computes 1day block maxima from daily precip file
   if opt==0:
      print("writing rx1day.nc .....")
      cdo.yearmax(input=pre_file, output=base_name+'_'+'rx1day.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearmax(input=pre_file, returnArray=v_name))
      return(tmp)

def run_rx3day(pre_file, v_name, base_name, opt):
   # computes 3day block maxima from daily precip file
   if opt==0:
      print("writing rx3day.nc .....")
      cdo.yearmax(input='-runsum,3 '+pre_file, output=base_name+'_'+'rx3day.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearmax(input='-runsum,3 '+pre_file, returnArray=v_name))
      return(tmp)

def run_rx5day(pre_file, v_name, base_name, opt):
   # computes 5day block maxima from daily precip file
   if opt==0:
      print("writing rx5day.nc .....")
      cdo.yearmax(input='-runsum,5 '+pre_file, output=base_name+'_'+'rx5day.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearmax(input='-runsum,5 '+pre_file, returnArray=v_name))
      return(tmp)

def run_prcptot(pre_file, v_name, base_name, opt):
   # computes total yearly precip (all days) from daily precip file
   if opt==0:
      print("writing prcptot.nc .....")   
      cdo.yearsum(input=pre_file, output=base_name+'_'+'prcptot.nc', options='-L')
      return;
   else:
      run_prcptot.tmp = np.squeeze(cdo.yearsum(input=pre_file, returnArray=v_name))
      return(run_prcptot.tmp)

def run_sdii(pre_file, v_name, base_name, opt):
   # computes simple daily intensity index (average rainfall amount on wetdays)
   if opt==0:
      print("writing sdii.nc .....")
      cdo.yearmean(input='-setrtomiss,0,0.999 '+pre_file, output=base_name+'_'+'sdii.nc', options='-L')
      return;
   else:
      tmp = np.squeeze(cdo.yearmean(input='-setrtomiss,0,0.999 '+pre_file, returnArray=v_name))
      return(tmp)

############################################### simple percentile based indices

def run_r95p(pre_file, v_name, base_name, opt):
   # computes how much rain per year falls above the 95p from daily pre files
   if opt==0:
      print("writing r95p.nc .....")
      cdo.yearsum(input='-mul '+pre_file+' -gtc,0 -sub '+pre_file+' r95p_file.nc', output='r95p.nc', options='-L')
      return;
   else:
      run_r95p.tmp = np.squeeze(cdo.yearsum(input='-mul '+pre_file+' -gtc,0 -sub '+pre_file+' r95p_file.nc', returnArray=v_name))
      return(run_r95p.tmp)

def run_r99p(pre_file, v_name, base_name, opt):
   # computes how much rain per year falls above the 99p from daily pre files
   if opt==0:
      print("writing r99.nc .....")
      cdo.yearsum(input='-mul '+pre_file+' -gtc,0 -sub '+pre_file+' r99p_file.nc', output='r99p.nc', options='-L')
      return;
   else:
      run_r99p.tmp = np.squeeze(cdo.yearsum(input='-mul '+pre_file+' -gtc,0 -sub '+pre_file+' r99p_file.nc', returnArray=v_name))
      return(run_r99p.tmp)

def run_r95ptot(base_name, opt):
   # computes how much (%) the 95p days contribute to yearly total - this must be run AFTER other rain percentile functions
   if opt==0:
      print("writing r95ptot.nc .....")
      cdo.mulc(100,input=' -div r95p.nc '+base_name+'_'+'prcptot.nc', output=base_name+'_'+'r95ptot.nc', options='-L')
      return;
   else:
      tmp = (run_r95p.tmp/run_prcptot.tmp)*100
      return(tmp)

def run_r99ptot(base_name, opt):
   # computes how much (%) the 99p days contribute to yearly total - this must be run AFTER other rain percentile functions
   if opt==0:
      print("writing r99ptot.nc .....")
      cdo.mulc(100,input=' -div r99p.nc '+base_name+'_'+'prcptot.nc', output=base_name+'_'+'r99ptot.nc', options='-L')
      return;
   else:
      tmp = (run_r99p.tmp/run_prcptot.tmp)*100
      return(tmp)

