# -*- coding: UTF-8 -*-
import paramiko, threading, sys, time, os

lock = threading.Lock()


def SSH(ip, user, pwd, port=36000, timeout=3, cmd='vmstat|sed -n 3p'):
    print("Start try ssh => %s" % ip)
    # ssh远程登陆执行vmstat获取资源信息
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username=user, password=pwd, timeout=timeout)
        print("[%s] Login %s => %s " % (ip, user, pwd))
        print("[%s] exec : %s" % (ip, cmd))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # print("[%s] exec result : %s" % (ip, stdout.read().decode()))
        result = stdout.read()
    except Exception as e:
        print("[%s] Error %s => %s" % (ip, user, pwd))
        print(e)
        return False
    else:
        ssh.close()
    # 将资源信息写入文件2,加锁
    if lock.acquire(True):
        try:
            f = open("./2", "a")
            # print(result)
            f.write("%s %s %s\n" % (
                ip, result.decode().strip("\n"), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            f.close()
        finally:
            lock.release()


def checkip(ip):
    if '.' not in ip:
        return False
    elif ip.count('.') != 3:
        return False
    else:
        flag = True
        t_ip = ip.split('.')
        for s in t_ip:
            try:
                s_num = int(s)
                if 0 <= s_num <= 255:
                    pass
                else:
                    flag = False
            except:
                flag = False
        return flag


if __name__ == '__main__':
    #处理非法ip
    dline = {}
    t_iplist = []
    new_iplist = []
    try:
        file1 = open("./1", "r")
        for line in file1:
            t_iplist.append(line.split('\t')[0])
            dline[line.split('\t')[0]] = line.strip("\n")
    except Exception as e:
        print(e)
    else:
        file1.close()

    s_iplist = set(t_iplist)
    it = iter(s_iplist)
    while True:
        try:
            x = next(it)
            #print("x:%s" % x)
            if checkip(x):
                new_iplist.append(x)
        except StopIteration:
            break
    #print(new_iplist)
    #print(dline)

    # 从文件1获得ip信息多线程获取资源信息
    t_list = []
    for IP in new_iplist:
        User = dline[IP].split('\t')[1]
        pwd = dline[IP].split('\t')[2]
        # print(User,pwd)
        t = threading.Thread(target=SSH, args=(IP, User, pwd.strip("\n")))
        t.start()
        t_list.append(t)
    for t in t_list:
        t.join()

    # 合并文件
    file2 = open("./2")
    for line2 in file2:
        if line2.strip("\n") != '':
            # print("line2 :%s" % line2)
            ip2, info = line2.split(' ', 1)
            if ip2 in dline:
                # print(ip2, info)
                dline[ip2] = dline[ip2] + '\t' + info.strip('\n')
    print(dline)
    file1 = open("./1", "w")
    file1.write(
        ' \t\t\t\t\t-----------memory---------- ---swap-- -----io---- -system-- '
        '------cpu-----\n \t\t\t\t\tr  b   swpd   free   buff '
        ' cache   si   so    bi    bo   in   cs us sy id wa st\n')
    for key in dline:
        file1.write(dline[key] + "\n")
    file1.close()
    file2.close()
