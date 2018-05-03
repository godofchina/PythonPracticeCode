#coding=utf-8
from xmlrpclib import ServerProxy, Fault
from os.path import join, abspath, isfile
from SimpleXMLRPCServer import SimpleXMLRPCServer
from urlparse import urlparse
import sys

SimpleXMLRPCServer.allow_reuse_address = 1
MAX_HISTORY_LENGTH = 6
UNHANDLED = 100
ACCESS_DENIED = 200

class UnhanledQuery(Fault):
    '''
    无法处理query请求时使用此异常
    '''
    def __init__(self, message="Couldn't handle the query"):
        Fault.__init__(self, UNHANDLED, message)


class AccessDenied(Fault):
    '''
    当客户尝试访问被禁用的资源时抛出此异常
    '''
    def __init__(self, message="Access Denied"):
        Fault.__init__(self, ACCESS_DENIED, message)

def inside(dir, name):
    '''
    检查用户指定的文件是否存在指定目录
    '''
    dir = abspath(dir)
    name = abspath(name)

    return name.startswith(join(dir, ''))

def getPort(url):
    '''
    从指定的url中解析出端口号
    '''
    netloc = urlparse(url)[1]
    port = netloc.split(':')

    return int(port[1])

class Node:
    def __init__(self, url, dirname, secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.know = set()

    def query(self, query, history = []):
        try:
            return self._handle(query)
        except UnhanledQuery:
            history = history + [self.url]
            if len(history) > MAX_HISTORY_LENGTH:
                return self._broadcast(query, history)

    def _handle(self, query):
        '''
        处理查询请求
        '''
        dir = self.dirname
        name = join(dir, query)
        if not isfile(name): raise UnhanledQuery
        if not inside(dir, name): raise AccessDenied

        with open(name) as file:
            content = file.read()
        return content

    def hello(self, other):
        '''
        添加临节点到当前节点列表中
        '''
        self.know.add(other)
        return 0

    def fetch(self, query, secret):
        '''
        获取文件内容
        '''
        if secret != self.secret: raise
        result = self.query(query)
        f = open(join(self.dirname, query),'w')
        f.write(result)
        f.close()
        return 0
    
    def _start(self):
        '''
        启动服务
        '''
        simpleRPCServer = SimpleXMLRPCServer(("", getPort(self.url)), logRequests = False)
        simpleRPCServer.register_instance(self)
        simpleRPCServer.serve_forever()

    def _broadcast(self, query, history):
        '''
        广播
        '''
        for other in self.konw.copy():
            if other in history: 
                continue
            try:
                s = ServerProxy(other)
                return s.query(query, history)
            except Fault, f:
                if f.faultCode == UNHANDLED:
                    pass
                else:
                    self.know.remove(other)
        raise UnhanledQuery

def main():
    url, directory, secret = sys.argv[1:]
    n = Node(url, directory, secret)
    n._start()

if __name__ == '__main__': 
    main()