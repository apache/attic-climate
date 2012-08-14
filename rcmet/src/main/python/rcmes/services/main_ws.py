from bottle import route, run
import list_vars_in_file
import find_latlon_var
import find_time_var
import decode_model_times as dmt
import run_rcmes_processing

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



if __name__ == "__main__":
    run(host='localhost', port=8082)
    
