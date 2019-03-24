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
    for id, line in enumerate(proc.stdout):
        #yield highlight(line, BashLexer(), HtmlFormatter())
        yield f"data:{highlight(line, BashLexer(), HtmlFormatter())}\n"
        if id == 1:
            yield "event:progress\ndata:10\n\n"
        elif id == 4:
            yield "event:progress\ndata:30\n\n"
        elif id == 6:
            yield "event:progress\ndata:50\n\n"
        elif id == 12:
            yield "event:progress\ndata:70\n\n"

    return_code = proc.wait()
    yield f"event:exit\ndata:{return_code}\n\n"

def stream_template(template_name, **context):
        app.update_template_context(context)
        t = app.jinja_env.get_template(template_name)
        rv = t.stream(context)
        return rv

@app.route('/conda-index')
def stream_conda_template():
    cmd = ['sh', 'do.sh']
    proc = run_command(cmd)
    return flask.Response(stream_template('template_command.html', 
                                          header='Indexing conda channel',
                                          result=output(proc),
                                          proc=proc))


@app.route('/commands/stream')
def stream():
    cmd = ['sh', 'do.sh']
    proc = run_command(cmd)
    return flask.Response(output(proc), mimetype='text/event-stream')

@app.route('/conda-event')
def stream_conda_event():
    return flask.render_template('template_command_event.html', header='Indexing conda channel')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
#root = File('./index.html')
#root.putChild(b"pip", File("./pip"))
#root.putChild(b"commands", WSGIResource(reactor, reactor.getThreadPool(), app))
#factory = Site(root)
#endpoint = endpoints.TCP4ServerEndpoint(reactor, 5000)
#endpoint.listen(factory)
#reactor.run()
