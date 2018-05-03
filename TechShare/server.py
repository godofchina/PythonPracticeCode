from SimpleXMLRPCServer import SimpleXMLRPCServer
s = SimpleXMLRPCServer(("",4242))

def twice(x):
    return x * x

s.register_function(twice)
s.serve_forever()