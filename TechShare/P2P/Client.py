#coding=utf-8
from xmlrpclib import ServerProxy, Fault
from cmd import Cmd
from random import choice
from string import lowercase
from Server import Node, UNHANDLED
from threading import Thread
from time import sleep
import sys
HEAD_START = 0.1
SECRET_LENGTH = 100

def randomString(length):
    '''
    生成随机字符串
    '''
    chars = []
    letters = lowercase[:26]
    while length > 0:
        length -= 1
        chars.append((choice(letters)))
    return ''.join(chars)

class Client(Cmd):
    '''
    下载客户端
    '''
    def __init__(self, url, dirname, urlfile):
        self.prompt = "> " # 命令行提示符
        Cmd.__init__(self)
        self.secret = randomString(SECRET_LENGTH)
        node = Node(url, dirname, self.secret)
        thread = Thread(target = node._start)
        thread.setDaemon(1)
        thread.start()
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        for line in open(urlfile):
            line = line.strip()
            self.server.hello(line)

    def do_fetch(self, arg):
        '''
        获取资源
        '''
        try:
            self.server.fetch(arg, self.secret)
        except Fault, f:
            if f.faultCode != UNHANDLED:
                raise
            print "Couldn't find the file", arg

    def do_exit(self, arg):
        '''
        退出
        '''
        print 'bye'
        sys.exit()

    # do_EOR = do_exit

def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.cmdloop()

if __name__ == '__main__':
    main()