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
from bottle import route, run, post, redirect, debug 

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
		<p>Please selecte the metric you will use.</p>
		<p>Enter the metric name into the URI, preceded by "/".
		A sample URI might read .../rcmet/metrics/calc_rms </p>
		<p> Metrics with one variable: 
		"calc_stdev" to return standard deviation</p>
		<p> Metrics with two variables: 
		"calc_annual_cycle_means" to return monthly means,
		"calc_annual_cycle_std" to return monthly standard deviation,
		"calc_annual_cycle_domain_means" to return monthly domain means,
		"calc_annual_cycle_domain_std" to return monthly standard deviation,
		"calc_bias" to return mean difference,
		"calc_bias_dom" to return domain mean difference,
		"calc_difference" to return difference,
		"calc_mae" to return mean absolute error,
		"calc_rms" to return root mean square error,
		"calc_rms_dom" to return domain root mean square error,
		"calc_temporal_pat_cor" to return temporal pattern correlation,
		"calc_pat_cor" to return pattern correlation,
		"calc_anom_cor" to return anomaly correlation,
		"calc_nash_sutcliff" to return Nash-Sutcliff coefficient of efficiency,
		"calc_pdf" to return probability distribution function.</p>
		<p> Metrics with three variables: 
		"calc_anom_cor" to return anomaly correlation</p>
		</body>
		<html>'''

#CHECK THIS WHOLE FUNCTION TO MAEKE SURE IT WORKS

#creates introductory page to explain how to use bottle
@route('/rcmet/metrics/<metric_name>')
def basic_info(metric_name):
	if metric_name in how_many_var:
		return "For metric %s , you need %d variables, which will represent: %s" 
			%(metric_name, how_many_var[metric_name], name_of_var[metric_name][:]),
			'''<p>Will you enter variables (which are arrays) through the command line or 
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
	"calc_rms" : 2,
	"calc_rms_dom" : 2,
	"calc_temporal_pat_cor" : 2,
	"calc_pat_cor" : 2,
	"calc_anom_cor" : 2,
	"calc_nash_sutcliff" : 2,
	"calc_pdf" : 2,
	"calc_anom_cor" : 3
}		
	
#dictionary of metric names and the names of their variables. Needs to be filled in, but also will be helpful	
name_of_var={
	"calc_stdev":[],
	"calc_annual_cycle_means" :[],
	"calc_annual_cycle_std" :[],
	"calc_annual_cycle_domain_means" :[],
	"calc_annual_cycle_domain_std" :[],
	"calc_bias" :[],
	"calc_bias_dom" :[],
	"calc_difference" :[], 
	"calc_mae" :[],
	"calc_rms" :[],
	"calc_rms_dom" :[],
	"calc_temporal_pat_cor" :[],
	"calc_pat_cor" :[],
	"calc_anom_cor" :[],
	"calc_nash_sutcliff" :[],
	"calc_pdf" :[],
	"calc_anom_cor" :[]
}				
		
##########################################################################################
#getting arrays through the command line
##########################################################################################

#Tells the user how to send variables from the command line
@route('/rcmet/metrics/<metric_name>/commandline')
def command_line_offered_arrays(metric_name):
	return "please use your command line to POST a form with the array. Send either a "
		"file or serialized string. Name the form: array." 
		"Send the form to: http://.../rcmet/metrics/getting_array/(name of metric)\n"
		"Once the computer receives all variables, you will be redirected to the metrics"
		"portion of the website."
	
#this is the function that gets the array from the command line. The user will never see this page. They are automatically redirected
@route('/rcmet/metrics/getting_array/<metric_name>', method='POST')
def command_line_array(metric_name):
	count=1
	array=request.forms.get('array')
	if type(array)==str:
		array=pickle.loads(array)
	else: 
		array=pickle.load(array)

	name_the_array(count, array)
	
#NEED SOME SORT OF POST SYSTEM TO PICK UP THE RAW_INPUT
	another_array=raw_input("Will you send another array? [y/n]")
	if another_array==y:
		count=count+1
		if count<=how_many_var[metric_name]:
			redirect('/rcmet/metrics/'+metric_name+'/commandline')
		else:
			print "Too many arrays for this metric."
			redirect('/rcmet/metrics/'+<metric_name+'/calculate')

	if another_array==n:
		if count=how_many_var[metric_name]:
			redirect('/rcmet/metrics/'+metric_name+'/calculate')
		else:
			print "Too few arrays for this metric."
			redirect('/rcmet/metrics/'+metric_name+'/commandline')

#this function basically names the arrays and publishes them to the entire module
#I used global for these variabels because it makes it possible for the user to submit 
#their variables on one page, through one function or another and no matter what means 
#they use to submit them, I can then run the metrics the same way for both because the 
#variables are already global

def name_the_array(count, array)	
	if count==1:
		array_name="array1"
		array1=array
		global array1
	if count==2:
		array_name="array2"
		array2=array
		global array2
	if count==3:
		array_name="array3"
		array3=array
		global array3
	print "variable received. Defined as %s. Will represent %s" 
		% (array_name, name_of_var[metric_name][count-1])


##if I global the count, it might be easier to have someone send one variable via online
##and get another through RCMED, or vice versa. If having a count is even the most 
##practical way to do this

##########################################################################################
#getting variables through RCMED
##########################################################################################

#this whole section is messy right now. I am mostly avoiding it out of fear

@route('/rcmet/metrics/<metric_name>/RCMEDdata')
def explain_dynamic_links(metric_name):
	return show_possible_metrics(), '''<html>
		<head> Possible Data Parameters to Choose From </head>
		<body>
		<p>#LOOK UP AND ENTER THE PARAMETERS!</p>
		<p>Writing a URI:</p>
		<p>your URI will read http.../rcmet/metrics/RCMEDdata/(ID of parameter 1)/
		(start time)/(end time)/(ID parameter 2)/(start time)/(end time)/
		(ID of parameter 3)/(start time)/(end time)</p>
		<p>Only enter as many parameters as you need. Do not end 
		URI with a slash.</p>
		</body>
		</html>'''
	
#DO THE ARRAYS FROM RCMED NEED PICKLE TOO?

#MAKE THIS ONE FUNCTION THAT CAN REPEAT THREE TIMES MAX		
#or do something that makes it less redundant and ugly. 

def get_arrays_from_dyn_links():
	try:	
		#a uri for metrics w/ 3 arrays obtained via Dynamic Links
		@route('/rcmet/metrics/<metric_name>/RCMEDdata/<IDone>/<stone>/<etone>/<IDtwo>/'+
			'<sttwo>/<ettwo>/<IDthree>/<stthree>/<etthree>') 
		def three_arrays(metric_name,IDone,stone,etone,IDtwo,sttwo,ettwo,IDthree,
			stthree,etthree):
			try:
				method=getattr(CAMERONS_CLASS, WHATEVER_FUNCTION_GETS_THE_ARRAYS)
				array1=method(IDone,stone,etone)
				array2=method(IDtwo,sttwo,ettwo)
				array3=method(IDthree,stthree,etthree)
				global array1
				global array2
				global array3
				redirect('/rcmet/metrics/<metric_name>/calculate')
				
			except TypeError:
				return ("Too many/too few values entered. Please enter only BLANK or",
					'''<a href="/rcmet/metrics/<metric_name>/RCMEDdata">Return to main page</a>''')	
		
		@route('/rcmet/metrics/<metric_name>/RCMEDdata/<IDone>/<stone>/<etone>/<IDtwo>/'+
			'<sttwo>/<ettwo>') 
		def two_arrays(metric_name,IDone,stone,etone,IDtwo,sttwo,ettwo):
			try:
				method=getattr(CAMERONS_CLASS, WHATEVER_FUNCTION_GETS_THE_ARRAYS)
				array1=method(IDone,stone,etone)
				array2=method(IDtwo,sttwo,ettwo)
				global array1
				global array2
				
			except TypeError:
				return ("Too many/too few values entered. Please enter only BLANK or",
					'''<a href="/rcmet/metrics/<metric_name>/RCMEDdata">Return to main page</a>''')
				
		@route('/rcmet/metrics/RCMEDdata/<IDone>/<stone>/<etone>') 
		def two_arrays(metric_name,IDone,stone,etone):
			try:
				method=getattr(CAMERONS_CLASS, WHATEVER_FUNCTION_GETS_THE_ARRAYS)
				array1=method(IDone,stone,etone)
				global array1

			except TypeError:
				return ("Too many/too few values entered. Please enter only BLANK or",
					'''<a href="/rcmet/metrics/<metric_name>/RCMEDdata">Return to main page</a>''')	

	except AttributeError:
		return ("The selected function doesn't exist. Please enter a new one or", 
			'''<a href='/rcmet/metrics/<metric_name>/RCMEDdata'>
			Return to main page</a>''')	
	
	except ValueError:
		return ("Invalid variable. Please make sure the variables ARE IN THIS FORMAT!!! or",
			'''<a href='/rcmet/metrics/<metric_name>/RCMEDdata'>
			Return to main page</a>''')	

##########################################################################################
#running the metrics
##########################################################################################
#this function actually runs the metrics
@route('/rcmet/metrics/<metric_name>/calculate')
def run_metrics(metric_name):
	
	try:
		if how_many_var[metric_name]==3
			try:
				method=getattr(mtx,metric_name)
				return mtx.method.__doc__, "This metric %s, with 3 variables (%s) entered" 
					" as %s, yields:" % (metric_name, name_of_var[metric_name][:],
					FIGURE OUT HOW TO NAME ARRAYS),str(method(array1, array2, array3)),
				
		if how_many_var[metric_name]==2
			try:
				method=getattr(mtx,metric_name)
				return mtx.method.__doc__, "This metric %s, with 2 variables (%s) entered" 
					" as %s, yields:" % (metric_name, name_of_var[metric_name][:],
					FIGURE OUT HOW TO NAME ARRAYS), str(method(array1,array2))
		
		if how_many_var[metric_name]==1
			try:
				method=getattr(mtx,metric_name)
				return mtx.method.__doc__, "This metric %s, with 1 variable (%s) entered" 
					" as %s, yields:" % (metric_name, name_of_var[metric_name][:],
					FIGURE OUT HOW TO NAME ARRAYS), str(method(array1))
			
#"figure out how to name arrays" refers to me wanted to come up with a system
#that's going to give each array a description (picked by the user), so that they are 
#better identified than array1, array2, etc.
#My function will still call them array1,2,3 because it's standardized, but they will have
#some sort of name attached to then somehow that the user will be able to identify them by. 
#*by which the user will be able to identify them.* Whatever. 

##########################################################################################
#final commands to tie everything together
##########################################################################################

#runs the function that runs the metrics
run_metrics()

#final function starts up bottle at http://localhost:8080
run(host='localhost', port=8080)





