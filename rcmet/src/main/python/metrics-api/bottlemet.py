'''
##########################################################################################
#
# Module to create a user interface for RCMET statistical metrics
#    
##########################################################################################
'''

##########################################################################################
#setting up bottle and a framework for calling metrics
##########################################################################################

#sets up bottle and necessary methods.
from bottle import route, run, post, request, redirect, debug 

#temporary quick-fix to track errors, not for publication 
debug(True)

#imports metrics from RCMET
import rcmes.metrics as mtx
		
##########################################################################################
#First parts of the User Interface
##########################################################################################

#basic first page. Explanation could be more comprehensive
@route('/rcmet/metrics')	
def show_possible_metics():
	return '''<html>
		<head> RCMET Metrics through Bottle </head>
		<body>
		<p>Please select the metric you will use.</p>
		
		<p> Metrics with one variable: 
		<a href='/rcmet/metrics/calc_stdev'>"calc_stdev" to return standard deviation</a>
		</p>
	
		<p> Metrics with two variables: 
		<a href='/rcmet/metrics/calc_annual_cycle_means'>"calc_annual_cycle_means" to 
		return monthly means</a>
		<a href='/rcmet/metrics/calc_annual_cycle_std'>""calc_annual_cycle_std" to return 
		monthly standard deviation</a>	
		<a href='/rcmet/metrics/calc_annual_cycle_domain_means'>"calc_annual_cycle_domain_
		means" to return monthly domain means</a>	
		<a href='/rcmet/metrics/calc_annual_cycle_domain_std'>"calc_annual_cycle_domain_
		std" to return monthly standard deviation</a>	
		<a href='/rcmet/metrics/calc_bias'>"calc_bias" to return mean difference</a>	
		<a href='/rcmet/metrics/calc_bias_dom'>"calc_bias_dom" to return domain mean 
		difference</a>	
		<a href='/rcmet/metrics/calc_difference'>"calc_difference" to return difference
		</a>
		<a href='/rcmet/metrics/calc_mae'>"calc_mae" to return mean absolute error</a>	
		<a href='/rcmet/metrics/calc_mae_dom'>"calc_mae_dom" to return domain mean 
		difference over time</a>
		<a href='/rcmet/metrics/calc_rms'>"calc_rms" to return root mean square error
		</a>	
		<a href='/rcmet/metrics/calc_rms_dom'>"calc_rms_dom" to return domain root mean 
		square error</a>	
		<a href='/rcmet/metrics/calc_temporal_pat_cor'>"calc_temporal_pat_cor" to return 
		temporal pattern correlation</a>
		<a href='/rcmet/metrics/calc_pat_cor'>"calc_pat_cor" to return pattern correlation
		</a>
		<a href='/rcmet/metrics/calc_anom_cor'>"calc_anom_cor" to return anomaly 
		correlation</a>
		<a href='/rcmet/metrics/calc_nash_sutcliff'>"calc_nash_sutcliff" to return 
		Nash-Sutcliff coefficient of efficiency</a>
		<a href='/rcmet/metrics/calc_pdf'>"calc_pdf" to return probability distribution 
		function</a>
		
		<p> Metrics with three variables:
		<a href='/rcmet/metrics/calc_anom_corn'>"calc_anom_cor" to return anomaly 
		correlation</a> </p>
		</body>
		<html>'''

#CHECK THIS WHOLE FUNCTION TO MAKE SURE IT WORKS

#creates introductory page to explain how to use bottle
@route('/rcmet/metrics/<metric_name>')
def basic_info(metric_name):
	
	#provision for tracking # of variables later on
	global count
	count=0
		
	if metric_name in how_many_var:
		return "For metric %s , you need %d variable(s), which will represent: %s" %(metric_name, 
			how_many_var[metric_name], name_of_var[metric_name][:]),
			'''<html>
			<body>
			<p>Will you enter variables (which are arrays) through the command line or 
			will you search the RCMES Database?</p>
			<a href="/rcmet/metrics/"+ metric_name+"/commandline">
			command line</a>
			<a href="/rcmet/metrics/"+metric_name+"/RCMEDdata">
			RCMED</a>
			</body>
			</html>'''
	
	else:
		return "The metric you entered doesn't exist."
	

		
##########################################################################################
#error-catching dictionaries (I'm not sure this was the best way to go, 
#but I didn't have any other ideas)
##########################################################################################

#dictionary of metric_names and their number of variables. Useful later on
how_many_var={
	"calc_stdev" :1,
	"calc_annual_cycle_means" : 2,
	"calc_annual_cycle_std" : 2,
	"calc_annual_cycle_domain_means" : 2,
	"calc_annual_cycle_domain_std" : 2,
	"calc_bias" : 2,
	"calc_bias_dom" : 2,
	"calc_difference" : 2,
	"calc_mae" : 2,
	"calc_mae_dom" :2,
	"calc_rms" : 2,
	"calc_rms_dom" : 2,
	"calc_temporal_pat_cor" : 2,
	"calc_pat_cor" : 2,
	"calc_anom_cor" : 2,
	"calc_nash_sutcliff" : 2,
	"calc_pdf" : 2,
	"calc_anom_corn" : 3
}		
	
#dictionary of metric names and the names of their variables. Needs to be filled in, but also will be helpful	
name_of_var={
	"calc_stdev":['t1'],
	"calc_annual_cycle_means" :['data','time'],
	"calc_annual_cycle_std" :['data','time'],
	"calc_annual_cycle_domain_means" :['data','time'],
	"calc_annual_cycle_domain_std" :['data','time'],
	"calc_bias" :['t1','t2'],
	"calc_bias_dom" :['t1','t2'],
	"calc_difference" :['t1','t2'], 
	"calc_mae" :['t1','t2'],
	"calc_mae_dom" : ['t1','t2'],
	"calc_rms" :['t1','t2'],
	"calc_rms_dom" :['t1','t2'],
	"calc_temporal_pat_cor" :['t1','t2'],
	"calc_pat_cor" :['t1','t2'],
	"calc_anom_cor" :['t1','t2'],
	"calc_nash_sutcliff" :['t1','t2'],
	"calc_pdf" :['t1','t2'],
	"calc_anom_corn" :['t1','t2','t4']
}				

#two lists that will help with user explanation later; so much better than global variables	
names_of_arrays=[]		

list_of_arrays=[]
		
##########################################################################################
#getting arrays through the command line
##########################################################################################

#Tells the user how to send variables from the command line
@route('/rcmet/metrics/<metric_name>/commandline')
def command_line_offered_arrays(metric_name):
	
	if how_many_var[metric_name]-count<=0:
		print "You have already submitted all the needed variables for this metric."
		redirect('/rcmet/metrics/'+metric_name+'/calculate')
	else:
		return "please use your command line to POST a form with the array. Send either a",
			" file or serialized string. Name the form: array. Include also, a form that ",
			"names the array. Call this form name. A sample would be array=<array_here> ",
			"and name=<array_name_here>. Send the form to: http://.../rcmet/metrics/",
			"getting_array/(name of metric)\n Once the computer receives all variables, ",
			"you will be redirected to the metrics portion of the website.",
			"Currently, you have submitted %d variable(s) and need %d more. The next ",
			"variable you submit will represent the variable %s in %s" %(count, 
			(how_many_var[metric_name]-count),name_of_var[metric_name][count], metric_name)
	
#this function  gets the array from the command line. The user will never see this page.
@route('/rcmet/metrics/getting_array/<metric_name>', method='POST')
def command_line_array(metric_name):
	
	array=request.forms.get('array')
	array_name=request.forms.get('name')
	if type(array)==str:
		array=pickle.loads(array)
	else:
		try: 
			array=pickle.load(array)
		except #NAME THE ERROR!
			print "The form you sent contains an invalid data format. Send only a file",
				" or serialized string."
	
	#much shorter, and cleaner later on
	list_of_arrays.append(array)
	names_of_arrays.append(array_name)
	
	print "Variable received as %s. Will represent %s" % (array_name, 
		name_of_var[metric_name][count-1])
	
	#uses the command line to ask the user if they want more input
	another_array=raw_input("Will you send another array on the command line? [y/n]")
	if another_array=='y':
		count=count+1
		global count #TEST THIS!!
		if count<how_many_var[metric_name]:
			redirect('/rcmet/metrics/'+metric_name+'/commandline')
		else:
			print "Too many arrays for this metric."
			redirect('/rcmet/metrics/'+metric_name+'/calculate')

	if another_array=='n':
		if count==how_many_var[metric_name]:
			redirect('/rcmet/metrics/'+metric_name+'/calculate')
		else:
			print "Too few arrays for this metric."
			redirect('/rcmet/metrics/'+metric_name+'/commandline')

##########################################################################################
#getting variables through RCMED
##########################################################################################

#explains how to enter information into a dynamic link
@route('/rcmet/metrics/<metric_name>/RCMEDdata')
def explain_dynamic_links(metric_name):
	return show_possible_metrics(), '''<html>
		<head> Possible Data Parameters to Choose From </head>
		<body>
		<p>#LOOK UP AND ENTER THE PARAMETERS!</p>
		<p>Writing a URI:</p>
		<p>your URI will read http.../rcmet/metrics/(metric_name)/RCMEDdata/
		(ID of parameter)/(start time)/(end time)/(string that describes your array></p>
		<p>Please enter one variable at a time.</p>
		</body>
		</html>''',
		"Currently, you have submitted %d variable(s) and need %d more. The next variable ",
		"you submit will represent the variable %s in %s" %(count, 
		(how_many_var[metric_name]-count),name_of_var[metric_name][count], metric_name)
	
@route('/rcmet/metrics/<metric_name>/RCMEDdata/<IDone>/<stone>/<etone>/<array_name>') 
def get_arrays_from_RCMED(metric_name,IDone,stone,etone):
	
	if how_many_var[metric_name]-count==0:
		print "You've already submitted all variables for this function."
		redirect('/rcmet/metrics/'+metric_name+'/calculate')
	
	else:		
		try:
			method=getattr(CAMERONS_CLASS, WHATEVER_FUNCTION_GETS_THE_ARRAYS)
			array=method(IDone,stone,etone)
			list_of_arrays.append(array)
			names_of_arrays.append(array_name)
			count=count+1
			global count
	
		#in case the user searches for the disneyland function or something weird like that
		except AttributeError:
			return ("There is not metric matches your parameters. ",
				"Please enter new parameters", 
				'''<a href='/rcmet/metrics/<metric_name>/RCMEDdata'>
				Return to main page</a>''')	
		
		#my next goal is to add more error handlers here. 

##########################################################################################
#running the metrics
##########################################################################################

#this function actually runs the metrics
@route('/rcmet/metrics/<metric_name>/calculate')
def run_metrics(metric_name):
	method=getattr(mtx, metric_name)
	
	if how_many_var[metric_name]==1:
		return explain_metric(metric_name), str(method(list_of_arrays[0]))
			
	if how_many_var[metric_name]==2:
		return explain_metric(metric_name), str(method(list_of_arrays[0], list_of_arrays[1]))
			
	if how_many_var[metric_name]==3:
		return explain_metric(metric_name), 
			str(method(list_of_arrays[0], list_of_arrays[1], list_of_arrays[2]))
		

def explain_metric(metric_name):
	return getattr(method,'__doc__'), "This metric %s, with %d variable(s)--%s--entered as %s ",
		"respectively, yields:" % (metric_name, how_many_var[metric_name],
		name_of_var[metric_name][:],names_of_arrays[:])

##########################################################################################
#final command to start bottle
##########################################################################################

#final function starts up bottle at http://localhost:8080
run(host='localhost', port=8080)

##########################################################################################
#notes and things that could change
#
#	1.Bottle is set to run on 'localhost:8080' 
#
#	2.The dictionaries may need to be added to/deleted
#
#	3.None of the class RCMED methods or parameters are listed
#
#	4.need to add an option for users to go from /commandline to /RCMEDdate
#
#	5.add more error handling 
#
##########################################################################################

