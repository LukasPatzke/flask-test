from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.web.proxy import ReverseProxyResource
from twisted.web.resource import Resource

class DynamicProxy(ReverseProxyResource):
    def __init__(self, port):
        ReverseProxyResource.__init__(self, 'localhost', port, b'')

class Root(Resource):
    def getChild(self, name, request):
        return DynamicProxy(int(name))

site = Site(Root())
endpoint = endpoints.TCP4ServerEndpoint(reactor, 80)
endpoint.listen(site)
reactor.run()