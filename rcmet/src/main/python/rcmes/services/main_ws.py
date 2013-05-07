"""Module that demonstrates how to initialize the RESTful web services that 
power the RCMET GUI"""

from bottle import route, response, run, static_file, hook
import list_vars_in_file
import find_latlon_var
import find_time_var
import decode_model_times as dmt
import run_rcmes_processing
import dataset_helpers
import directory_helpers

@route('/')
@route('/index.html')
def index():
    return "<a href='/hello'>Go to Hello World page</a>"

@route('/hello')
def hello():
    return "Hello World!"

@route('/api/status')
def api_status():
    return {'status':'online', 'key':'value'}

@route('/static/evalResults/<filename>')
def get_eval_result_image(filename):
    return static_file(filename, root="/tmp/rcmet")

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

if __name__ == "__main__":
    run(host='localhost', port=8082)
    
