# coding: utf-8

import paramiko
import re
import time

# 定义一个类，表示一台远端linux主机
class LinuxSSH(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, ip, username, password, timeout=60000):
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout
        # transport和chanel
        self.t = ''
        self.chan = ''
        # 链接失败的重试次数
        self.try_times = 3

    # 调用该方法连接远程主机
    def connect(self):
        while True:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                self.t = paramiko.Transport(sock=(self.ip, 22))
                self.t.connect(username=self.username, password=self.password)
                self.chan = self.t.open_session()
                self.chan.settimeout(self.timeout)
                self.chan.get_pty()
                self.chan.invoke_shell()
                # 如果没有抛出异常说明连接成功，直接返回
                print u'连接%s成功' % self.ip
                # 接收到的网络数据解码为str
                print self.chan.recv(65535).decode('utf-8')
                return
            # 这里不对可能的异常如socket.error, socket.timeout细化，直接一网打尽
            except Exception, e1:
                if self.try_times != 0:
                    print u'连接%s失败，进行重试' % self.ip
                    self.try_times -= 1
                else:
                    print u'重试3次失败，结束程序'
                    exit(1)

    # 断开连接
    def close(self):
        self.chan.close()
        self.t.close()

    # 发送要执行的命令
    def send(self, cmd, iswait=False, breakreg=r'.*', timeout=60):
        start = time.time()
        cmd += '\r'
        # 通过命令执行提示符来判断命令是否执行完成
        finish = re.compile(breakreg)
        result = ''
        # 发送要执行的命令
        self.chan.send(cmd)
        # 回显很长的命令可能执行较久，通过循环分批次取回回显
        while True:
            time.sleep(0.5)
            ret = self.chan.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            print ret
            if iswait is False:
                return result
            elif finish.search(ret):
                return result
            else:
                end = time.time()
                if end - start > timeout:
                    print cmd+":执行超时!("+timeout+"s)"
                    result += cmd+":执行超时!("+timeout+"s)"
                    return result


def excuteRbcCompileSh(ip, port, user, password):
    sshhost = LinuxSSH(ip, port, user, password)
    sshhost.connect()
    sshhost.send('cd /diskgcp/HH/RBC2', False)
    sshhost.send('pwd', False)
    sshhost.send('./compile.sh RBS_HHRBC2 RBS_HHRBC2-4.1.4/', True, breakreg=r'The RBS_.* build was .*', timeout=480)
    sshhost.close()

# 链接正常的情况
if __name__ == '__main__':
    excuteRbcCompileSh('172.16.33.205', 'root', 'dsutc11c')