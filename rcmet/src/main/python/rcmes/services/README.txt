RCMET Client API Web Service README
===========================================================

Prerequisites:

 * Python 2.6+ with easy_install
 * Bottle (http://bottlepy.org) Web Framework 

Usage:

 ./python main_ws.py


Hints:

  Changing the port Bottle runs on
  --------------------------------
  The port Bottle starts up on can be changed by editing
  the last line in the ./main_ws.py file as follows:

  if __name__ == "__main__":
    run(host='localhost', port=*NEWPORT*)


API Documentation:
=================================================================

Extract Model File Variables
--------------------------------
http://<webserviceUrl>/list/vars/"<PATH>"

  INPUTS: 
    PATH: the fully qualified path to the model file to use. Note 
          that the path must be enclosed in double quotes.

  RETURN:
    SUCCESS: {"variables": ["tas", "level", "lon", "time", "lat"]}
    FAILURE: []   <-- should probably be {}


Extract Model Latitude and Longitude Variables and Bounds
---------------------------------------------------------
http://<webserviceUrl>/list/latlon/"<PATH>"

  INPUTS: 
    PATH: the fully qualified path to the model file to use. Note 
    	  that the path must be enclosed in double quotes.

  RETURN:
    SUCCESS: {"latMax": "42.24", "success": 1, "latname": "lat", 
              "lonMax": "60.28", "lonMin": "-24.64", 
	      "lonname": "lon", "latMin": "-45.76"}
    FAILURE: ?


Extract Model Time Variable and Bounds
--------------------------------------
http://<webserviceUrl>/list/time/"<PATH>"

  INPUTS: 
    PATH: the fully qualified path to the model file to use. Note 
          that the path must be enclosed in double quotes.

  RETURN:
    SUCCESS:  {"start_time": "1989-01-15 00:00:00", 
    	       "timename": "time", "success": 1, 
	       "end_time": "2008-12-15 00:00:00"}
    FAILURE: ?
