import flask
import subprocess

from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from twisted.web.server import Site
from twisted.web.static import File
from twisted.internet import reactor, endpoints
from twisted.web.wsgi import WSGIResource
from twisted.web.resource import Resource

import jinja2

app = flask.Flask(__name__)
app.debug = True

#@app.route('/')
#def root():
#    return flask.send_from_directory(directory='.', filename='index.html')
def run_command(cmd):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return proc
def output(proc):
    for line in proc.stdout:
        yield highlight(line, BashLexer(), HtmlFormatter())


def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        rv = t.stream(context)
        return rv

@app.route('/conda-index')
def stream():
    cmd = ['sh', 'do.sh']
    proc = run_command(cmd)
    return flask.Response(stream_template('template_command.html', 
                                          header='Indexing conda channel',
                                          result=output(proc),
                                          proc=proc))
    
root = File('./index.html')
root.putChild(b"pip", File("./pip"))
root.putChild(b"commands", WSGIResource(reactor, reactor.getThreadPool(), app))
factory = Site(root)
endpoint = endpoints.TCP4ServerEndpoint(reactor, 5000)
endpoint.listen(factory)
reactor.run()
