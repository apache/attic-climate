'''
##########################################################################################
#
# Module to create a web service for RCMET statistical metrics
#	 
##########################################################################################
'''




##########################################################################################
#setting up bottle and importing metrics
##########################################################################################

#sets up bottle and necessary methods.
from bottle import route, run, post, request, redirect, debug 

#temporary quick-fix to track errors, not for publication 
debug(True)

#imports pickle
import pickle

#imports metrics from RCMET
import rcmes.metrics as mtx




##########################################################################################
#error-catching dictionaries 
##########################################################################################

#dictionary of MetricNames and their number of variables. Useful later on
HowManyVariables={
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
	
#dictionary of metric names and the names of their variables.
NameOfVariables={
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

#two lists that will help with user explanation later

ArrayNames=[]	   

ListOfArrays=[]
	
	
	
##########################################################################################

#Running the metrics through interactive web pages

##########################################################################################



##########################################################################################
#First parts: introduction and identification of user's needs
##########################################################################################

#basic first page. Explanation could be more comprehensive
@route('/rcmet/metrics/online')	
def ShowPossibleMetrics():
	'''
	Returns a page in html that allows the user to select a metric through links
	'''
	return '''<html>
		<head> RCMET Metrics through Bottle </head>
		<body>
		<p>Please select the metric you will use.</p>
		
		<p> Metrics with one variable: 
		<a href='/rcmet/metrics/online/calc_stdev'>"calc_stdev" to return standard deviation</a>
		</p>
	
		<p> Metrics with two variables: 
		<a href='/rcmet/metrics/online/calc_annual_cycle_means'>"calc_annual_cycle_means" to return monthly means</a>
		<a href='/rcmet/metrics/online/calc_annual_cycle_std'>""calc_annual_cycle_std" to return monthly standard deviation</a>  
		<a href='/rcmet/metrics/online/calc_annual_cycle_domain_means'>"calc_annual_cycle_domain_ means" to return monthly 
		domain means</a>   
		<a href='/rcmet/metrics/online/calc_annual_cycle_domain_std'>"calc_annual_cycle_domain_std" to return monthly standard 
		deviation</a>	
		<a href='/rcmet/metrics/online/calc_bias'>"calc_bias" to return mean difference</a>	
		<a href='/rcmet/metrics/online/calc_bias_dom'>"calc_bias_dom" to return domain mean difference</a>	 
		<a href='/rcmet/metrics/online/calc_difference'>"calc_difference" to return difference</a>
		<a href='/rcmet/metrics/online/calc_mae'>"calc_mae" to return mean absolute error</a>	
		<a href='/rcmet/metrics/online/calc_mae_dom'>"calc_mae_dom" to return domain mean difference over time</a>
		<a href='/rcmet/metrics/online/calc_rms'>"calc_rms" to return root mean square error
		</a>	
		<a href='/rcmet/metrics/online/calc_rms_dom'>"calc_rms_dom" to return domain root mean square error</a>	
		<a href='/rcmet/metrics/online/calc_temporal_pat_cor'>"calc_temporal_pat_cor" to return temporal pattern correlation</a>
		<a href='/rcmet/metrics/online/calc_pat_cor'>"calc_pat_cor" to return pattern correlation</a>
		<a href='/rcmet/metrics/online/calc_anom_cor'>"calc_anom_cor" to return anomaly correlation</a>
		<a href='/rcmet/metrics/online/calc_nash_sutcliff'>"calc_nash_sutcliff" to return Nash-Sutcliff coefficient of 
		efficiency</a>
		<a href='/rcmet/metrics/online/calc_pdf'>"calc_pdf" to return probability distribution function</a>
		
		<p> Metrics with three variables:
		<a href='/rcmet/metrics/online/calc_anom_corn'>"calc_anom_cor" to return anomaly correlation</a> </p>
		</body>
		<html>'''

#creates introductory page to explain how to use bottle
@route('/rcmet/metrics/online/<MetricNameHere>')
def VariableSubmission(MetricNameHere):
	'''
	Returns a page in html that allows the user to choose between submitting variables on the command line or searching 
	RCMED
	'''	  
	
	global MetricName
	
	MetricName=MetricNameHere
	
	if MetricName in HowManyVariables:
		return "For metric %s , you need %d variable(s), which will represent: %s" %(MetricName, 
			HowManyVariables[MetricName], NameOfVariables[MetricName][:]), '''<html>
			<body>
			<p>Will you enter variables (which are arrays) through the command line or 
			will you search the RCMES Database?</p>
			<a href="/rcmet/metrics/online/commandline">command line</a>
			<a href="/rcmet/metrics/online/rcmed">RCMED</a>
			</body>
			</html>''',
			'''<a href='/rcmet/metrics/online/methods'>Run Methods</a>'''
	
	else:
		return "The metric you entered doesn't exist."


##########################################################################################
#getting arrays through the command line
##########################################################################################

#Tells the user how to send variables from the command line
@route('/rcmet/metrics/online/commandline')
def ArraysFromCommandLine():
	'''
	Explains to the user how to submit a variable through POST on the command line
	'''
	if HowManyVariables[MetricName]-count<=0:
		print "You have already submitted all the needed variables for this metric."
		redirect('/rcmet/metrics/online/calculate')
	else:
		return "Please use your command line to POST a form with the array. Send either a pickled file or serialized ",
		"string. Name the form: array. Include also, a form that describes/names the array. Call this form: name. A ",
		"sample would be array=array_here and name=array_name_here. Send the form to: ",
		"http://.../rcmet/metrics/<metric_name>/commandline. Once the computer receives all variables, you may ", 
		"move on to the metrics portion of the website. Currently, you have submitted %d variable(s) and need %d ",
		"more. The next variable you submit will represent the variable %s in %s" %(count, 
		(HowManyVariables[MetricName]-count),NameOfVariables[MetricName][count], MetricName)
	
#this function	gets the array from the command line
@route('/rcmet/metrics/online/commandline', method='POST') 
def ReceivingArrays():
	'''
	Uses the POST method to retrieve any arrays sent by the user, and proceed to deserialize them. Also adds each
	variable to the appropriate list, and proceeds to offer the user the option to add more variables or else move
	on to calculating the value of the metric;
	'''
		
	try:
		BottleMetrics.GetVariablesFromCommandLine()
			
		return "Variable received as %s. Will represent %s" % (ArrayNames[count-1], 
		NameOfVariables[MetricName][count-1]), "Submit more variables?",
		'''<a href='/rcmet/metrics/online/rcmed'>Online</a>''',
		'''<a href='/rcmet/metrics/online/commandline'>Command Line</a>''',
		'''<a href='/rcmet/metrics/online/calculate'>No More Variables</a>''',
		'''<a href='/rcmet/metrics/online/methods'>Run Methods</a>'''
	
	except pickle.UnpicklingError:
		return "This object cannot be unpickled. Send only a file or serialized string.",
		'''<a href='/rcmet/metrics/online/commandline'>Re-submit Variable</a>''',
		'''<a href='/rcmet/metrics/online/methods'>Run Methods</a>'''
		

##########################################################################################
#getting variables through RCMED
##########################################################################################

#explains how to enter information into a dynamic link
@route('/rcmet/metrics/online/rcmed')
def QueryRcmed():
	'''
	Returns a page in html that explains to the user how to search RCMED for the desired arrays, and offers the
	user multiple forms in which to enter search parameters
	'''
	
	#I was unclear what type the dataset ID and paramID were supposed to be. This may need to change
	
	return "Currently, you have submitted %d variable(s) and need %d more. The next"\
	" variable you submit will represent the variable %s in %s" %(count, 
	(HowManyVariables[MetricName]-count),NameOfVariables[MetricName][count], MetricName),'''<html>
	<head> Query RCMED for Array Data </head>
	<body>
	<p>Enter the parameters into the appropriate boxes.</p>
	<form method="POST">
		<p>Dataset ID</p>
		<input name="datasetID"	 type="string" />
		<p>Parameter ID</p>
		<input name="paramID"	 type="string" />
		<p>latMin, float</p>
		<input name="latMin"	 type="float" />
		<p>latMax, float</p>
		<input name="latMax"	 type="float" />
		<p>lonMin, float</p>
		<input name="lonMin"	 type="float" />
		<p>lonMax, float</p>
		<input name="lonMax"	 type="float" />
		<p>startTime, datetime object</p>
		<input name="startTime"	 type="datetime" />
		<p>endTime, datetime object</p>
		<input name="endTime"	 type="datetime" />
		<p>cachedir, string</p>
		<input name="cachedir"	 type="string" />
		<p>Array Name, string</p>
		<input name="ArrayName"	 type="string" />
		<input type="Submit" /> </form>
	</body>
	</html>''' 
	
	
@route('/rcmet/metrics/online/rcmed', method='POST')
def GetVariablesFromDatabase():
	'''
	Gets data from forms, searches the database, processes the variables, and prompts the user to submit more.
	'''
	BottleMetrics.GetVariablesFromRcmed()	 


	return "Submit more variables?",'''<a href='/rcmet/metrics/online/rcmed'>Online</a>''',
	'''<a href='/rcmet/metrics/online/commandline'>Command Line</a>''',
	'''<a href='/rcmet/metrics/online/calculate'>No More Variables</a>''',
	'''<a href='/rcmet/metrics/online/methods'>Run Methods</a>'''


##########################################################################################
#running the metrics online
##########################################################################################

#this function actually runs the metrics
@route('/rcmet/metrics/online/calculate')
def Calculate(MetricName):
	'''
	Uses variables from the lists to return the answer for the metric. Also returns a brief description of the metric performed. 
	'''
		
	if HowManyVariables[MetricName]<count:
		return "You have too few variables to run this metric.",'''<a href='/rcmet/metrics/online/commandline'>Command Line</a>,
		<a href='/rcmet/metrics/online/rcmed'>Online</a>''','''<a href='/rcmet/metrics/online/methods'>Run Methods</a>'''
	
	else:
		return BottleMetrics.ExplainMetric(), str(result), '''<a href='/rcmet/metrics/online/methods'>Run Methods</a>''',
		'''<a href='/rcmet/metrics/online'>Start Over</a>'''
			
	
	'''<a href='/rcmet/metrics/online/methods'>Run Methods</a>'''
	
@route('/rcmet/metrics/online/methods')
def ChooseMethodOnline():
	'''
	Allows an online user to access any method in the class
	'''
	
	return "Which method?", '''<html>
	<a href='/rcmet/metrics/online/methods/Status'>Status</a>
	<a href='/rcmet/metrics/online/methods/ExplainMetric'>ExplainMetric</a>
	<a href='/rcmet/metrics/online/methods/VariableCount'>VariableCount</a>
	<a href='/rcmet/metrics/online/methods/ReturnResult'>ReturnResult</a>
	<a href='/rcmet/metrics/online/methods/CleanUp'>CleanUp</a>'''
	
@route('/rcmet/metrics/online/methods/<MethodName>)
def RunMethodOnline(MethodName):
	'''
	Runs any method in class MetricWebService() chosen by an online user
	'''
		
	MetricWebServiceMethod=getattr(BottleMetrics, MethodName)
	
	return BottleMetrics.MetricWebServiceMethod(), '''<a href='/rcmet/metrics/online'>Back to Beginning</a>'''
	

##########################################################################################	
##########################################################################################

#creating a class for the Web Service 

##########################################################################################
##########################################################################################

class MetricWebService(object):
	'''
	Class containing all of the necessary functions to find, process, and use the variables to run metrics. Also allows
	the user to see the state of the metric, i.e. how many variables have been entered. 
	'''
		
	def __init__(self):

		global count
		count=0

##########################################################################################

	def Status(self):
		'''
		Provides a standardized system for showing how many variables are submitted, allowing the user to 
		check their progress 
		'''
		print "For metric %s , you need %d variable(s): %s. Currently, you have submitted "\
		"%d variable(s) and need %d more. The values you have submitted, %s, will represent %s respectively." 
		%(MetricName, HowManyVariables[MetricName], NameOfVariables[MetricName][:], count, 
		(HowManyVariables[MetricName]-count),ArrayNames[:],NameOfVariables[MetricName][:])
		
		return "For metric %s , you need %d variable(s): %s. Currently, you have submitted "\
		"%d variable(s) and need %d more. The values you have submitted, %s, will represent %s respectively." 
		%(MetricName, HowManyVariables[MetricName], NameOfVariables[MetricName][:], count, 
		(HowManyVariables[MetricName]-count),ArrayNames[:],NameOfVariables[MetricName][:])
		
##########################################################################################

	def ExplainMetric(self):
		'''
		Provides a standardized means of returning a metric's docstring and thus describing the metric
		'''
		method=getattr(mt, MetricName)

		print method.__doc__

		return method.__doc__
##########################################################################################

	def VariableCount(self):
		'''
		Determines how many variables have been submitted, and if the right number has, this function runs the RunMetrics() method
		'''
			
		if HowManyVariables[MetricName]-count>0:
		
			print "Please add more variables"
			
			return "Please add more variables"
					
		if HowManyVariables[MetricName]-count<0:
			print "You have added too many variables"
			
			return "Please add more variabels"
			
		else:
			print "You have added all necessary metrics. The program will now run your metric."
			
			self.RunMetrics()
			

##########################################################################################
	
	def ProcessVariables(self, array, ArrayName):	
		'''
		adds the variables posted by the user to the appropriate lists, raises count to indicate this addition, and
		starts VariableCount()
		'''			
		ListOfArrays.append(array)
		ArrayNames.append(ArrayName)
			
		global count
		count=count+1
			
		print "Variable received as %s. Will represent %s" % (ArrayName, 
		NameOfVariables[MetricName][count-1])
			
		self.VariableCount()
		
##########################################################################################

	def GetVariablesFromCommandLine(self):	
		'''
		Gets array and array name from forms, deserializes them with unpickle, and runs ProcessVariables()
		'''	
		
		if HowManyVariables[MetricName]-count>0:
			array=request.forms.get('array')
			ArrayName=request.forms.get('name')
			
			if type(array)==str:
				array=pickle.loads(array)	   
			
			else:
				array=pickle.load(array)
		
			self.ProcessVariables(array, ArrayName)
		
		else:
			self.VariableCount()
	
##########################################################################################
	
	def GetVariablesFromRcmed(self):	
		'''
		Gets search parameters from forms, runs a search of RCMED, and returns the array mdata
		'''
		
		if HowManyVariables[MetricName]-count>0:
		
			import rcmes.db as db
	
			datasetID=request.forms.get('datasetID')
			paramID=request.forms.get('paramID')
			latMin=request.forms.get('latMin')
			latMax=request.forms.get('latMax')
			lonMin=request.forms.get('lonMin')
			lonMax=request.forms.get('lonMax')
			startTime=request.forms.get('startTime')
			endTime=request.forms.get('endTime')
			cachedir=request.forms.get('cachedir')
	
			ArrayName=request.forms.get('name')				
					
			try:
			
				db.extract_data_from_db(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir)
				
				#I don't think this will work
				array=mdata
				
				self.ProcessVariables(array,ArrayName)
										
			except TypeError:
				print "One of your variables was not entered in the correct format or was not entered at all"
			
		else:
			self.VariableCount()	
			
##########################################################################################
	
	def GetVariables(self):
		'''
		Runs two links that connect with functions meant to handle the variables posted to the links
		'''
####################
		
		@route('/rcmet/metrics/get/variables/commandline', method='POST') 
		def VariablesPostedToCommandline():
			'''
			runs the method GetVariablesFromCommandLine() at the URL, allowing the user to post their forms to this url and have
			them handled by GetVariablesFromCommandLine().
			'''
			
			try:
				self.GetVariablesFromCommandLine()
					
			except pickle.UnpicklingError:
				print "This object cannot be unpickled. Send only a file or serialized string."
	

####################

		@route('/rcmet/metrics/get/variables/rcmed', method='POST')
		def GetVariablesFromRCMED(self):
			'''
			runs the method GetVariablesFromRcmed() at the URL, allowing the user to post their forms to this url and have
			them handled by GetVariablesFromRcmed().
			'''
			
			self.GetVariablesFromRcmed()	 
				
##########################################################################################
				
	def RunMetrics(self):
		'''
		Calls to metrics.py and runs the desired metric using variables submitted by the user. Returns a string of the 
		value returned by the metric
		'''
		
		print "Running metric"	
		  
		method=getattr(mtx, MetricName)
	
		global result
	
		if HowManyVariables[MetricName]==1:
			result=method(ListOfArrays[0])
			
		if HowManyVariables[MetricName]==2:
			result=method(ListOfArrays[0], ListOfArrays[1])
				
		if HowManyVariables[MetricName]==3:
			result=method(ListOfArrays[0], ListOfArrays[1], ListOfArrays[2])
		
##########################################################################################
		
	@route('/rcmet/metrics/commandline/return/result')
	def ReturnResult():
		'''
		links the result to a uri from which the user can easily fetch it. Note, the result is returned as a string
		'''	
	#If the result of the metrics is an array, I would recommend including a provision in 
	#ReturnResult() that pickles or somehow serializes the result, and then, upon getting 
	#the pickled string from the URL, the user could unpickle it and use it as an array. 	
	
		return str(result)
		
##########################################################################################

	def CleanUp(self, name):
		'''
		resets the lists, the count, and the variable MetricName back to zero, enabling a user to in effect start over, without
		re-creating the instance of the class. 
		'''
		
		global ArrayNames
		ArrayNames=[]
		
		global ListOfArrays
		ListOfArrays=[]
		
		global count
		count=0	
		
		global MetricName
		name=MetricName

##########################################################################################
#final commands to tie everything together 
##########################################################################################

#allows the command line user to remotely create an instance of the class
@route('/rcmet/metrics/commandline', method='POST')
def CreateAnInstance():
	'''
	Sets up a POST page that creates an instance of the class for a user on the command line. The user does not need
	to open this page for it to function; they need only post the name of the metric they want. 
	'''
	
	NameOfMetric=request.forms.get('NameOfMetric')
	
	global MetricName
	
	MetricName=NameOfMetric

	if name in HowManyVariables:
		BottleMetrics.GetVariables()
	
	else:
		print "The metric you entered, %s, does not exist" %name	



@route('/rcmet/metrics/commandline/methods', method='POST')
def RunAMethod():
	'''
	Allows a command line user to access any method in class MetricWebService() by sending a form
	'''
	MethodName=request.forms.get('MethodName')
	
	MetricWebServiceMethod=getattr(BottleMetrics, MethodName)
	
	BottleMetrics.MetricWebServiceMethod()
	 

BottleMetrics=MetricWebService()

#final function starts up bottle at http://localhost:8080
#note: localhost:8080 may need to be changed eventually 
run(host='localhost', port=8080)




