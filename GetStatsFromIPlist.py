import paramiko, threading, sys, time, os


lock = threading.Lock()

def SSH(ip, port, user, pwd, timeout=3, cmd='vmstat|sed -n 3p'):
    print("Start try ssh => %s" % ip)
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, username=user, password=pwd, timeout=timeout)
        print("[%s] Login %s => %s " % (ip, user, pwd))
        print("[%s] exec : %s" % (ip, cmd))
        stdin, stdout, stderr = ssh.exec_command(cmd)
        #print("[%s] exec result : %s" % (ip, stdout.read().decode()))
        result = stdout.read()
    except Exception as e:
        print("[%s] Error %s => %s" % (ip, user, pwd))
        print(e)
        return False
    finally:
        ssh.close()
    if lock.acquire(True):
        try:
            file = open("./2", "a")
            file.write("%s %s %s\n" % (ip, result.decode().strip("\n"), time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
            file.close()
        finally:
            lock.release()

if __name__ == '__main__':
    file1 = open("./1")
    for line in file1:
        IP, Port, User, Passwd = line.split(' ')
        threading.Thread(target=SSH, args=(IP, Port, User, Passwd.strip("\n"))).start()
    file2 = open("./2")
    for line2 in file2:

    file1.close()
