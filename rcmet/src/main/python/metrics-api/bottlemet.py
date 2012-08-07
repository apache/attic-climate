'''
##########################################################################################
#
# Module to create a web service for RCMET statistical metrics
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

#imports pickle
import pickle

#imports metrics from RCMET
import rcmes.metrics as mtx
        
##########################################################################################
#First parts: introduction and identification of user's needs
##########################################################################################

#basic first page. Explanation could be more comprehensive
@route('/rcmet/metrics')    
def ShowPossibleMetrics():
    '''
    Returns a page in html that allows the user to select a metric through links
    '''
    return '''<html>
        <head> RCMET Metrics through Bottle </head>
        <body>
        <p>Please select the metric you will use.</p>
        
        <p> Metrics with one variable: 
        <a href='/rcmet/metrics/calc_stdev'>"calc_stdev" to return standard deviation</a>
        </p>
    
        <p> Metrics with two variables: 
        <a href='/rcmet/metrics/calc_annual_cycle_means'>"calc_annual_cycle_means" to return monthly means</a>
        <a href='/rcmet/metrics/calc_annual_cycle_std'>""calc_annual_cycle_std" to return monthly standard deviation</a>  
        <a href='/rcmet/metrics/calc_annual_cycle_domain_means'>"calc_annual_cycle_domain_ means" to return monthly 
        domain means</a>   
        <a href='/rcmet/metrics/calc_annual_cycle_domain_std'>"calc_annual_cycle_domain_std" to return monthly standard 
        deviation</a>   
        <a href='/rcmet/metrics/calc_bias'>"calc_bias" to return mean difference</a>    
        <a href='/rcmet/metrics/calc_bias_dom'>"calc_bias_dom" to return domain mean difference</a>  
        <a href='/rcmet/metrics/calc_difference'>"calc_difference" to return difference</a>
        <a href='/rcmet/metrics/calc_mae'>"calc_mae" to return mean absolute error</a>  
        <a href='/rcmet/metrics/calc_mae_dom'>"calc_mae_dom" to return domain mean difference over time</a>
        <a href='/rcmet/metrics/calc_rms'>"calc_rms" to return root mean square error
        </a>    
        <a href='/rcmet/metrics/calc_rms_dom'>"calc_rms_dom" to return domain root mean square error</a>    
        <a href='/rcmet/metrics/calc_temporal_pat_cor'>"calc_temporal_pat_cor" to return temporal pattern correlation</a>
        <a href='/rcmet/metrics/calc_pat_cor'>"calc_pat_cor" to return pattern correlation</a>
        <a href='/rcmet/metrics/calc_anom_cor'>"calc_anom_cor" to return anomaly correlation</a>
        <a href='/rcmet/metrics/calc_nash_sutcliff'>"calc_nash_sutcliff" to return Nash-Sutcliff coefficient of 
        efficiency</a>
        <a href='/rcmet/metrics/calc_pdf'>"calc_pdf" to return probability distribution function</a>
        
        <p> Metrics with three variables:
        <a href='/rcmet/metrics/calc_anom_corn'>"calc_anom_cor" to return anomaly correlation</a> </p>
        </body>
        <html>'''

#creates introductory page to explain how to use bottle
@route('/rcmet/metrics/<MetricName>')
def VariableSubmission(MetricName):
    '''
    Returns a page in html that allows the user to choose between submitting variables on the command line or searching 
    RCMED
    '''   
    #provision for tracking # of variables later on
    global count
    count=0
        
    if MetricName in HowManyVariables:
        return "For metric %s , you need %d variable(s), which will represent: %s" %(MetricName, 
            HowManyVariables[MetricName], NameOfVariables[MetricName][:]), '''<html>
            <body>
            <p>Will you enter variables (which are arrays) through the command line or 
            will you search the RCMES Database?</p>
            <a href="/rcmet/metrics/"+ MetricName+"/commandline">
            command line</a>
            <a href="/rcmet/metrics/"+MetricName+"/RCMEDdata">
            RCMED</a>
            </body>
            </html>'''
    
    else:
        return "The metric you entered doesn't exist."
    

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
#getting arrays through the command line
##########################################################################################

#Tells the user how to send variables from the command line
@route('/rcmet/metrics/<MetricName>/commandline')
def ArraysFromCommandLine(MetricName):
    '''
    Explains to the user how to submit a variable through POST on the command line
    '''
    if HowManyVariables[MetricName]-count<=0:
        print "You have already submitted all the needed variables for this metric."
        redirect('/rcmet/metrics/'+MetricName+'/calculate')
    else:
        print "Please use your command line to POST a form with the array. Send either a pickled file or serialized ",
        "string. Name the form: array. Include also, a form that describes/names the array. Call this form name. A ",
        "sample would be array=<array_here> and name=<array_name_here>. Send the form to: ",
        "http://.../rcmet/metrics/(name of metric)/commandline. Once the computer receives all variables, you will be ", 
        "redirected to the metrics portion of the website. Currently, you have submitted %d variable(s) and need %d ",
        "more. The next variable you submit will represent the variable %s in %s" %(count, 
        (HowManyVariables[MetricName]-count),NameOfVariables[MetricName][count], MetricName)
    
#this function  gets the array from the command line
@route('/rcmet/metrics/<MetricName>/commandline', method='POST')
def ReceivingArrays(MetricName):
    '''
    Uses the POST method to retrieve any arrays sent by the user, and proceed to deserialize them. Also adds each
    variable to the appropriate list, and proceeds to offer the user the option to add more variables or else move
    on to calculating the value of the metric;
    '''
        
    array=request.forms.get('array')
    ArrayName=request.forms.get('name')
    if type(array)==str:
        try:
            array=pickle.loads(array)
        except pickle.UnpicklingError:
            print "This object cannot be unpickled. Send only a file or serialized string."    
    else:
        try: 
            array=pickle.load(array)
        except pickle.UnpicklingError:
            print "This object cannot be unpickled. Send only a file or serialized string."
    
    #much shorter, and cleaner later on
    ListOfArrays.append(array)
    ArrayNames.append(ArrayName)
    
    print "Variable received as %s. Will represent %s" % (ArrayName, 
        NameOfVariables[MetricName][count-1])
    
    #uses the command line to ask the user if they want more input
    AnotherArray=raw_input("Will you send another array on the command line? [y/n]")
    if AnotherArray=='y':
        count=count+1
        global count
        if count<HowManyVariables[MetricName]:
            redirect('/rcmet/metrics/'+MetricName+'/commandline')
        else:
            print "Too many arrays for this metric."
            redirect('/rcmet/metrics/'+MetricName+'/calculate')

    if AnotherArray=='n':
        if count==HowManyVariables[MetricName]:
            redirect('/rcmet/metrics/'+MetricName+'/calculate')
        else:
            print "Too few arrays for this metric."
            redirect('/rcmet/metrics/'+MetricName)

##########################################################################################
#getting variables through RCMED
##########################################################################################

#explains how to enter information into a dynamic link
@route('/rcmet/metrics/<MetricName>/RCMEDdata')
def ExplainDynamicLinks(MetricName):
    '''
    Returns a page in html that explains to the user how to search RCMED for the desired arrays
    '''return '''<html>
        <head> Possible Data Parameters to Choose From </head>
        <body>
        <p>#LOOK UP AND ENTER THE PARAMETERS!</p>
        <p>Writing a URI:</p>
        <p>your URI will read http.../rcmet/metrics/(MetricName)/RCMEDdata/
        (ID of parameter)/(start time)/(end time)/(string that describes your array)</p>
        <p>Please enter one variable at a time.</p>
        </body>
        </html>''', "Currently, you have submitted %d variable(s) and need %d more. The next"\
        " variable you submit will represent the variable %s in %s" %(count, 
        (HowManyVariables[MetricName]-count),NameOfVariables[MetricName][count], MetricName)
    
@route('/rcmet/metrics/<MetricName>/RCMEDdata/<IDone>/<stone>/<etone>/<ArrayName>') 
def GetArraysRCMED(MetricName,IDone,stone,etone):
    '''
    Uses dynamic links to find values in RCMED, deserializes them, and allow to user to decide whether to add more or 
    go on to calculate the metrics. 
    '''
        
    if HowManyVariables[MetricName]-count==0:
        print "You've already submitted all variables for this function."
        redirect('/rcmet/metrics/'+MetricName+'/calculate')
    
    else:       
        try:
            method=getattr(CAMERONS_CLASS, WHATEVER_FUNCTION_GETS_THE_ARRAYS)
            array=method(IDone,stone,etone)
            ListOfArrays.append(array)
            ArrayNames.append(ArrayName)
            count=count+1
            global count
            
            return "Submit more variables?",'''<a href='/rcmet/metrics/'+MetricName+'/RCMEDdata'>Online</a>''',
            '''<a href='/rcmet/metrics/'+MetricName+'/commandline'>Command Line</a>''',
            '''<a href='/rcmet/metrics/'+MetricName+'/calculate'>No More Variables</a>''',
    
        #in case the user searches a function that does not exist  
        except AttributeError:
            return ("There is not metric matches your parameters. Please enter new parameters", 
            '''<a href='/rcmet/metrics/'+MetricName+'/RCMEDdata'>Return to intro page</a>''')  
        
        #my next goal is to add more error handlers here. 

##########################################################################################
#running the metrics
##########################################################################################

#this function actually runs the metrics
@route('/rcmet/metrics/<MetricName>/calculate')
def RunMetrics(MetricName):
    '''
    Uses variables from the lists to return the answer for the metric. Calls to the metrics in rcmes.metrics using 
    getattr. Also returns a brief description of the metric performed. 
    '''
    if HowManyVariables[MetricName]>count:
        return "You have too many variables to run this metric.",'''<a href='/rcmet/metrics'>Start Over</a>'''
    
    if HowManyVariables[MetricName]<count:
        return "You have too few variables to run this metric.",'''<a href='/rcmet/metrics/'+MetricName>Add More</a>'''

    else:

        method=getattr(mtx, MetricName)
    
        if HowManyVariables[MetricName]==1:
            return ExplainMetric(MetricName), str(method(ListOfArrays[0]))
            
        if HowManyVariables[MetricName]==2:
            return ExplainMetric(MetricName), str(method(ListOfArrays[0], ListOfArrays[1]))
            
        if HowManyVariables[MetricName]==3:
            return ExplainMetric(MetricName), str(method(ListOfArrays[0], ListOfArrays[1], ListOfArrays[2]))
        

def ExplainMetric(MetricName):
    '''
    Provides a standardized system for describing the metric operation, so the user understands what the answer means
    '''
    return "This metric %s, with %d variable(s)--%s--entered as %s respectively, "\
    "yields:" % (MetricName, HowManyVariables[MetricName], NameOfVariables[MetricName][:],
    ArrayNames[:])


##########################################################################################
#final command to start bottle
##########################################################################################

#final function starts up bottle at http://localhost:8080
run(host='localhost', port=8080)





##########################################################################################
#notes and things that could change
#
#   1.Bottle is set to run on 'localhost:8080' 
#
#   2.The dictionaries may need to be edited
#
#   3.None of the class RCMED methods or parameters are listed
#
#   4.need to add an option for users to go from /commandline to /RCMEDdate
#
#   5.add more error handling 
#
##########################################################################################

