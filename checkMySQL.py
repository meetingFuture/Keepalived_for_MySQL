#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: hailong.sun1982@gmail.com  at 2017.05

import sys
import os
import getopt
import MySQLdb
import logging
import filelock
import config
import subprocess
from MySQLib import LogMgr

dbhost=config.dbhost
dbport=config.dbport
dbuser=config.dbuser
dbpassword=config.dbpassword

def prt_log(func):

    def _deco(*args, **kwargs):
        ret = func(*args, **kwargs)
        log_inst = LogMgr("checkMySQL.log")
        for line in ret:
            log_inst.info("Func %s is called Msg: %s" % (func.__name__, line) )

    return _deco

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret_str = p.stdout.read()
    retval = p.wait()
    return ret_str 

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/tmp/kp_check.log',
                    filemode='a')

def get_gw():

    get_gw_cmd="""route -n|grep " UG "|awk '{ print $2 }'"""
    ret = run_cmd(get_gw_cmd).strip()
    return ret

def ping_host(host_addr):

    host_ip = host_addr
    ret = subprocess.call("ping -c 1 %s" % host_ip, shell=True, stdout=open(r'ping.temp','w'), stderr=subprocess.STDOUT) 
    return ret

def ping_gw():
    
    gw_ip = get_gw()
    # print gw_ip
    ping_ret = ping_host(gw_ip)
    if ping_ret == 0:
        return True
    else:
        return False

def checkMySQL():
    global dbhost
    global dbport
    global dbuser
    global dbpassword
        
    ping_gw_ret = ping_gw()
    if ping_gw_ret:
        shortargs='h:P:'
        opts, args=getopt.getopt(sys.argv[1:],shortargs)
        for opt, value in opts:
            if opt=='-h':
                dbhost=value
            elif opt=='-P':
                dbport=value
        db = instanceMySQL(dbhost, dbport, dbuser, dbpassword)
        st = db.ishaveMySQL()
    else:
        st = 1
    return st

class instanceMySQL:

    conn = None
    def __init__(self, host=None,port=None, user=None, passwd=None):
        self.dbhost= host
        self.dbport = int(port)
        self.dbuser = user
        self.dbpassword = passwd

    def ishaveMySQL(self):
        cmd="ps -ef | egrep -i \"mysqld\" | grep %s | egrep -iv \"mysqld_safe\" | grep -v grep | wc -l" % self.dbport
        mysqldNum = os.popen(cmd).read()
        cmd ="netstat -tunlp | grep \":%s\" | wc -l" % self.dbport
        mysqlPortNum= os.popen(cmd).read()

        if ( int(mysqldNum) <= 0):
            print "error"
            return False

        if ( int(mysqldNum) > 0 and  mysqlPortNum <= 0):
            return False
        return True

    def connect(self):
        try:

            self.conn=MySQLdb.connect(host="%s"%self.dbhost, port=self.dbport,user="%s"%dbuser, passwd="%s"%self.dbpassword)
            cursor = self.conn.cursor() 
            cursor.execute("select 1")
            cursor.close

        except Exception, e:

            return False

        return True

    def disconnect(self):

        if (self.conn):
            self.conn.close()
            self.conn = None


def main():
    log_obj = LogMgr('/etc/keepalived/scripts/checkMySQL.log')
    lockfile = config.lockfile
    lock = filelock.FileLock(lockfile)

    if lock:
        log_obj.info("File Locked sucessfull!")

    try:

        with lock.acquire(timeout=5):
            pass

    except filelock.timeout:
        log_obj.warn("get file lock timeout")
		
    log_obj.info("\ncheck MySQL started.....")

    if not ping_gw():
       gw_ip = get_gw()
       log_obj.info("Ping gateway %s failed" % gw_ip)
       sys.exit(1) 

    try:
        st=instanceMySQL(dbhost, dbport, dbuser, dbpassword)
        st_conn = st.connect()
    
        if st_conn :
            log_obj.info("MySQL check successfull, select 1 is ok!")
            sys.exit(0)
        else:
            log_obj.error("MySQL check failed, select 1 is failed!")
            sys.exit(1)
    except Exception, err:
        log_obj.error("MySQL connect failed, with error %s" % err) 
        sys.exit(1)

if __name__== "__main__":

    main()
