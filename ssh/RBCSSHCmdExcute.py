#-*- coding: utf-8 -*-
import paramiko
import threading
import getpass
import os
import sys
import traceback
import time

# 获取SSH连接的客户端
def _get_client(hostname, port, username, password,timeout = 10):
    port = int(port)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname,port,username,password, timeout=timeout)
    return client

# 获取SSH连接的SFTP
def _get_sftp(hostname, port, username, password):
    port = int(port)
    t = paramiko.Transport((hostname, port))
    t.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    return sftp

#SSH连接并执行指令
def ssh2CmdExcute(cmd,ignoreError,ip,port,username,passwd):
    try:
        result = True
        ssh = _get_client(ip, port, username, passwd)
        cmd = cmd.replace(',', '\n')     #如果采用,号分割则替换为换行
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print 'command:\'' + cmd + '\'exec successed!\tout:'

        if ignoreError!='true':
            print 'command:\'' + cmd + '\'exec successed!\tout:'
            out = stdout.readlines()
            err = stderr.readline()
            if err != '':
                print 'command:\'' + cmd + '\'exec failed!\terr:\n\t' + err
                print '%s\t服务器指令执行失败\n'% (ip)
                result = False
            else:
                print 'command:\'' + cmd + '\'exec successed!\tout:'
                stdout.read()
                # 屏幕输出
                for o in out:
                    print o,
                print '%s\t服务器指令执行完成\n'% (ip)
        else:
            print 'command:\'' + cmd + '\'exec successed!\tout:'
            out = stdout.readlines()
            err = stderr.readlines()
            for o in out:
              print '\n\t' + o
            for e in err:
              print '\n\t' + e
            print '%s\t服务器指令执行完成\n'% (ip)
        ssh.close()
        return result
    except Exception,e:
        msg = traceback.format_exc()
        print (msg)
        print '%s\t服务器连接失败，错误如下：'%(ip)
        print '\t'+str(e)
        return False

#清空远程Linux系统下的目录
def clearRemoteDir(remoteDir, hostname, port, username, password):
    delcommand = 'rm -rf ' + remoteDir
    createcommand = 'mkdir ' + remoteDir
    buildcmd = delcommand + ',' +createcommand
    result = ssh2CmdExcute(buildcmd, False, server_ip, server_port, server_user, server_passwd)
    return result

#上传Windows指定路径localDir至服务器路径remoteDir下
def scpUploadDir(localDir, remoteDir, hostname, port, username, password):
    sftp = _get_sftp(hostname, port, username, password)
    client = _get_client(hostname, port, username, password)
    localDir = localDir.replace('\\','/')
    for parent, dirnames, filenames in os.walk(localDir):
        parent = parent.replace('\\','/')
        if parent != localDir:
            parentname = parent.replace(localDir + '/','') + '/'
        else:
            parentname = ''
        remoteUploadDir = (remoteDir + '/' + parentname).replace('//','/')
        #循环每一层目录创建服务器中的目录结构
        for dirname in dirnames:
            remotepath = remoteUploadDir + dirname
            command = 'mkdir %s' % (remotepath)
            print command
            client.exec_command(command)
        #循环所有文件，上传文件
        for filename in filenames:
            localfile = os.path.join(parent, filename).replace('\\','/')
            localfilename = os.path.basename(localfile)
            remotefile = (remoteUploadDir + '/' + localfilename).replace('//', '/')
            print 'excute : scp %s %s' % (localfile, remotefile)
            time.sleep(0.5) #如果不设置延时存在上传文件错误，未找到原因
            sftp.put(localfile, remotefile)
            print 'success: scp %s %s' % (localfile, remotefile)
    sftp.close()
    client.close()
    return True

#下载远程文件到本地
def scpDownloadDir(localDir, remoteFile, hostname, port, username, password):
    sftp = _get_sftp(hostname, port, username, password)
    os.chdir(localDir)
    l_file = os.path.join(localDir, os.path.basename(remoteFile))
    sftp.get(remoteFile, l_file)
    sftp.close()
    return True


if __name__=='__main__':
    result = False
    try:
        if len(sys.argv) > 1:
            # 说明：
            # 如果采用命令行启动python脚本：
            # sys.argv[0] 为当前python脚本名称
            # sys.argv[1] 为当前python脚本执行函数类型，识别关键字包括：
            #     执行命令：EXCUTE；
            #     清空目录：CLEARDIR；
            #     上传目录：UPLOADDIR；
            #     下载文件：DOWNLOADFILE；
            # sys.argv[2] 远程SSH服务器IP；
            # sys.argv[3] 远程SSH服务器端口；
            # sys.argv[4] 远程SSH连接用户名；
            # sys.argv[5] 远程SSH连接密码；
            # 后续sys.argv[.]根据不同指令进行定义，具体参考以下说明
            cmdType = sys.argv[1]
            if cmdType == 'EXCUTE':
                if len(sys.argv) == 8:
                    server_ip = sys.argv[2]
                    server_port = sys.argv[3]
                    server_user = sys.argv[4]
                    server_passwd = sys.argv[5]
                    buildcmd = sys.argv[6]
                    ignoreError = sys.argv[7]
                    result = ssh2CmdExcute(buildcmd, ignoreError, server_ip, server_port, server_user, server_passwd)
                else:
                    print 'Excute SSHCmdExcute.ssh2CmdExcute() args length not 8'
                    result = False
            elif cmdType == 'CLEARDIR':
                if len(sys.argv) == 7:
                    server_ip = sys.argv[2]
                    server_port = sys.argv[3]
                    server_user = sys.argv[4]
                    server_passwd = sys.argv[5]
                    remoteDir = sys.argv[6]
                    result = clearRemoteDir(remoteDir,server_ip,server_port,server_user,server_passwd)
                else:
                    print 'Excute SSHCmdExcute.clearRemoteDir() args length not 7'
                    result = False
            elif cmdType == 'UPLOADDIR':
                if len(sys.argv) == 8:
                    server_ip = sys.argv[2]
                    server_port = sys.argv[3]
                    server_user = sys.argv[4]
                    server_passwd = sys.argv[5]
                    localDir = sys.argv[6]
                    remoteDir = sys.argv[7]
                    result = scpUploadDir(localDir, remoteDir,server_ip,server_port,server_user,server_passwd)
                else:
                    print 'Excute SSHCmdExcute.scpUploadDir() args length not 8'
                    result = False
            elif cmdType == 'DOWNLOADFILE':
                if len(sys.argv) == 8:
                    server_ip = sys.argv[2]
                    server_port = sys.argv[3]
                    server_user = sys.argv[4]
                    server_passwd = sys.argv[5]
                    localDir = sys.argv[6]
                    remoteDir = sys.argv[7]
                    result = scpDownloadDir(localDir, remoteDir, server_ip, server_port, server_user, server_passwd)
                else:
                    print 'Excute SSHCmdExcute.scpUploadDir() args length not 8'
                    result = False
            else:
                print 'Unexpected Command Type :'+ cmdType;
        else:
            print '系统未传递参数变量!执行main函数中默认参数'
            #buildtsrccmd = 'cd /ycp/TSRS-FSPU/TSRS-0.1.0/TSRS-FSPU/impDayly/,/ycp/TSRS-FSPU/TSRS-0.1.0/TSRS-FSPU/impDayly/make.sh'
            server_ip = '10.2.39.67'
            server_port = 22
            server_user = 'cbr2'
            server_passwd = 'password'
            #result = ssh2CmdExcute(buildtsrccmd,'',server_ip,server_port,server_user,server_passwd)

            # localDir = 'D:/03-Temp/RBC/upload'
            # remoteDir ='/home/cbr2/temp/'
            # result = clearRemoteDir(remoteDir,server_ip,server_port,server_user,server_passwd)#清空文件临时文件夹
            # result = scpUploadDir(localDir, remoteDir,server_ip,server_port,server_user,server_passwd)#上传文件至文件夹
            #remoteDir = '/export/'
            #result = clearRemoteDir(remoteDir,server_ip,server_port,server_user,server_passwd)#清空export文件夹
            # buildtsrccmd ='rm -rf export/,cd /export,mkdir -p HH/RBCC1,mv /home/cbr2/temp/RBS_HHRBC1-dev /export/HH/RBCC1'
            # result = ssh2CmdExcute(buildtsrccmd,'',server_ip,server_port,server_user,server_passwd)

            # localDir = 'D:/03-Temp/RBC/sh'
            # remoteDir ='/export/HH/RBCC1/'
            # result = scpUploadDir(localDir, remoteDir,server_ip,server_port,server_user,server_passwd)#上传文件至文件夹
            # buildtsrccmd = 'cd /export/HH/RBC1/RBS_HHRBC1-dev/RBS_HHRBC1/,pwd,crc ConfigInfo.CI >& T.log,cat T.log,rm -rf T.log'
            # buildtsrccmd = 'cd /export/HH/RBC1/RBS_HHRBC1-dev/RBS_HHRBC1/,crc ConfigInfo.CI'
            # result = ssh2CmdExcute(buildtsrccmd,False,server_ip,server_port,server_user,server_passwd)#执行脚本
            buildtsrccmd = 'pgrep  buildProduct'
            # buildtsrccmd = 'cd /export/HH/RBC1/,./compile.sh RBS_HHRBC1 RBS_HHRBC1-dev '
            # buildtsrccmd = 'cd /export/HH/RBC1/,./compile.sh RBS_HHRBC1 RBS_HHRBC1-dev >dev2.txt'
            count = 1
            while True:
                result = ssh2CmdExcute(buildtsrccmd, 'true', server_ip, server_port, server_user, server_passwd)  # 执行脚本
                count += 1
                time.sleep(2)
                print count
                print result
            # print("download compile result")
            localDir = 'D:/03-Temp/RBC/download'
            remoteDir = '/export/HH/RBCC1/RBS_HHRBC1-dev/RBS_HHRBC1/distribution/package/rbs.RBS_HHRBCdev2.setup'
            # result = scpDownloadDir(localDir, remoteDir, server_ip, server_port, server_user, server_passwd)
            # remoteDir = '/export/HH/RBCC1/RBS_HHRBC1-dev/RBS_HHRBC1/distribution/doc/productReport.txt'
            # result = scpDownloadDir(localDir, remoteDir, server_ip, server_port, server_user, server_passwd)
            # result =ssh2CmdExcute('readConfig –ereadConfig –e','',server_ip,server_port,server_user,server_passwd)
            print("****the end")
    except Exception as e:
        msg = traceback.format_exc()
        print (msg)
        result = False
    finally:
        print result
