from tasks import a_long_task
import time

def application(env, start_response):
    #import pdb;pdb.set_trace()
    if not 'favicon' in env['REQUEST_URI']:
        a_long_task.spool(foo="bar",time=time.time())
    start_response('200 OK', [('Content-Type','text/html')])
    return [b"Hello World"]

