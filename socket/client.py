# coding=utf-8
import socket               # 导入 socket 模块

s = socket.socket()         # 创建 socket 对象
host = socket.gethostname() # 获取本地主机名
port = 6299                # 设置端口好

s.connect((host, port))
s.send("发送链接请求");
print s.recv(1024)
s.close()