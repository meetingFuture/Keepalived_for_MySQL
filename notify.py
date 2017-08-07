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
from MySQLib import LogMgr
import pdb 
import time
from MySQLib import send_mail
from MySQLib import send_sms
from distutils.version import LooseVersion

_MySQL_Version = config.MySQL_Version
if  _MySQL_Version == "5.7": 

    preSlaveSQL="set global innodb_flush_log_at_trx_commit=0;set global sync_binlog=0;set global super_read_only=1; set global read_only=1;start slave;"
    preMasterSQL="set global innodb_flush_log_at_trx_commit=1;set global sync_binlog=1;set global super_read_only=0; set global read_only=0;start slave;"
    resartSlaveSQL="set global super_read_only=0;stop slave; start slave;set global super_read_only=1;"

elif _MySQL_Version == "5.6":

    preSlaveSQL="set global innodb_flush_log_at_trx_commit=0;set global sync_binlog=0;set global read_only=1;start slave;"
    preMasterSQL="set global innodb_flush_log_at_trx_commit=1;set global sync_binlog=1; set global read_only=0;start slave;"
    resartSlaveSQL="stop slave; start slave;"

else:
    preSlaveSQL="set global innodb_flush_log_at_trx_commit=0;set global sync_binlog=0;set global super_read_only=1; set global read_only=1;start slave;"
    preMasterSQL="set global innodb_flush_log_at_trx_commit=1;set global sync_binlog=1;set global super_read_only=0; set global read_only=0;start slave;"
    resartSlaveSQL="set global super_read_only=0;stop slave; start slave;set global super_read_only=1;"
 
import subprocess

def run_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret_str = p.stdout.read()
    retval = p.wait()
    return ret_str 

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/kp.log',
                filemode='a')



# class MySQLBase:

#         def __init__(self, DB_HOST='192.168.11.123', DB_PORT=3306, DB_USER='xxxx', DB_PWD='1111', DB_NAME='mysql'):


#                 self.DB_HOST = DB_HOST 
#                 self.DB_PORT = DB_PORT
#                 self.DB_USER = DB_USER
#                 self.DB_PWD = DB_PWD
#                 self.DB_NAME = DB_NAME


#                 self.conn = self.getConnection()

#         def getConnection(self):


#                 return MySQLdb.Connect( 
#                     host=self.DB_HOST, 
#                     port=self.DB_PORT, 
#                     user=self.DB_USER,
#                     passwd=self.DB_PWD, 
#                     db=self.DB_NAME,
#                     charset='utf8'
#                     )


#         def query(self, sql):

#                 try:
#                     cursor=self.conn.cursor() 
#                     cursor.execute(sql) 
#                     returnData=cursor.fetchall() 
#                     cursor.close() 
#                     return returnData
#                 except Exception, err:
#                     return err

#         def queryone(self, sql):

#                 try:
#                     cursor=self.conn.cursor()
#                     cursor.execute(sql)
#                     returnData=cursor.fetchone()
#                     cursor.close()
#                     return returnData
#                 except Exception, err:
#                     return err

#         def update(self, sql): 

#                 try:
#                     cursor=self.conn.cursor() 
#                     cursor.execute(sql) 
#                     self.conn.commit() 
#                     cursor.close() 
#                 except Exception, err:
#                     return err

#         def delete(self, sql):
#                 try:
#                     cursor=self.conn.cursor()
#                     cursor.execute(sql)
#                     self.conn.commit()
#                     cursor.close()
#                 except Exception, err:
#                     return err

#         def insert(self,sql):

#                 try:
#                     cursor = self.conn.cursor()
#                     cursor.execute(sql)
#                     self.conn.commit()
#                 except Exception, err:
#                     return err

#         def commitTransaction(self):
#                 self.conn.commit()

#         def closeCursor(self):
#                 cursor = self.conn.cursor()
#                 cursor.close()

#         def lastinsertid(self):
#                 cursor = self.conn.cursor()
#                 cursor.execute("select LAST_INSERT_ID()")
#                 data = cursor.fetchone()
#                 cursor.close()
#                 return data

# class MySQLSwitchHandler(MySQLBase):

#         def makeMaster(self):
#                 cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

#                 if  preMasterSQL.strip() != '' :
#                         cursor.execute(preMasterSQL)
#                         for r in cursor.fetchall():
#                                 print r

#                 cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

#                 query="show slave status"

#                 cursor.execute(query)
#                 for row in cursor.fetchall():

#                         if row['Slave_IO_Running'] == 'Yes':
#                                 #print "stop slave io_thread for channel '%s'" %row['Channel_Name']
#                                 cursor.execute("stop slave io_thread for channel  '%s'" % row['Channel_Name'])
#                                 logging.warning("stop slave io_thread for channel '%s'" % row['Channel_Name'])

#         def makeSlave(self):
#                 cursor = self.conn.cursor()

#                 if preSlaveSQL.strip() !='' :
#                         cursor.execute(preSlaveSQL)
#                         for r in cursor.fetchall():
#                                 print r
#                 cursor.close()
#                 self.conn.commit()
#                 cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
#                 query="show slave status"

#                 cursor.execute(query)
#                 for row in cursor.fetchall():
#                         #print row
#                         if row['Slave_IO_Running'] == 'No':
#                                 cursor.execute("start slave for channel '%s'" % row['Channel_Name'])
#                                 logging.warning("start slave for channel '%s'" % row['Channel_Name'])

class DBase:

	conn = None
	def __init__(self, host=None,port=None, user=None, passwd=None):
		self.dbhost= host
		self.dbport = port
		self.dbuser = user
		self.dbpassword = passwd
		self.conn=MySQLdb.connect(host="%s"%self.dbhost, port=self.dbport,user="%s"%dbuser, passwd="%s"%self.dbpassword)
		

	def restartSlave(self):

                cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(resartSlaveSQL)
		cursor.close()

	def makeMaster(self):
                try:
                    cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
		    
                    if  preMasterSQL.strip() != '' :
                        cursor.execute(preMasterSQL)
		    cursor.close()
                    return True, preMasterSQL
                except Exception, err:
                    return False, err
			
	def makeSlave(self):
		cursor = self.conn.cursor()
		
                if preSlaveSQL.strip() !='' :
                    cursor.execute(preSlaveSQL) 
                    #for r in cursor.fetchall():
                    #    print r			
		cursor.close()
                return preSlaveSQL
	

	def disconnect(self):
		if (self.conn):
			self.conn.close()
			self.conn = None

def get_slave_hosts(slave_suffix):

    host_list = []
    # 获取主机名前缀
    import socket
    host_prefix = socket.gethostname().split('.')[0].replace('mysql00','mysql').replace('mysql01','mysql')

    for _suffix in slave_suffix:
        slave_host_str = """%s%s""" % ( host_prefix, _suffix.strip() )
        host_list.append( slave_host_str)
    return host_list

if __name__== "__main__":

    import socket
    log_obj = LogMgr('/etc/keepalived/scripts/checkMySQL.log')
    lockfile = config.lockfile
    lock = filelock.FileLock(lockfile)
    local_hostname = socket.gethostname()

    if lock:
        log_obj.info("File Locked sucessfull!")

    try:

        with lock.acquire(timeout=5):
            #print "lock acquire"
            pass

    except filelock.timeout:
        log_obj.warn("get file lock timeout")

    logging.info(sys.argv)
    dbhost = config.dbhost
    dbport = config.dbport
    dbuser = config.dbuser
    dbpassword = config.dbpassword

    mail_host = config.mail_host
    mail_user = config.mail_user
    mail_pass = config.mail_pass
    mail_postfix = config.mail_postfix
    slave_suffix_list = config.slave_suffix
    sms_list = config.sms_list

    sub = config.sub
    to_list=config.mailto_list


    try:
        db = DBase(dbhost, dbport, dbuser, dbpassword)
    
        MySQL_role = sys.argv[3].upper()
        mail_content = " HOSTNAME: %s \nHOST: %s \n Keepalived Switch to %s "  % (local_hostname, dbhost, MySQL_role)

        if MySQL_role == 'MASTER':
    
            log_obj.warn("\nGet Master State: After 5 seconds become Master.....")
            time.sleep(5)
            
            try:

                mybool, ret = db.makeMaster()
                if mybool:

                    mysql_slave_list = get_slave_hosts(slave_suffix_list)
                    #print mysql_slave_list
                    for _hostname in mysql_slave_list:
                        db_slave = DBase(_hostname, dbport, dbuser, dbpassword)
                        db_slave.restartSlave()

                    warning_log = "\nMySQL> %s" % ret
                    log_obj.warn(warning_log)
                    mail_content = mail_content +  "\n" + warning_log
                    # 短信报警
                    sms_ret = send_sms( mail_content, sms_list )
                    warning_log = "SMS sending..." 
                    log_obj.warn(warning_log)
                    warning_log = "SMS content %s: " % mail_content
                    log_obj.warn(warning_log)
                    warning_log = "SMS send result: %s" % sms_ret[2]
                    log_obj.warn(warning_log)
                    # 邮件报警
                    send_mail(sub, mail_content, to_list, mail_host, mail_user, mail_pass, mail_postfix) 

                else:
                    log_obj.warn(str(ret))

            except Exception, err:

                log_obj.warn(str(err))


        if MySQL_role == "BACKUP" or MySQL_role == "FAULT":

            log_obj.warn("\nGet Backup Stat: Current become Slave.....")

            try:

                ret = db.makeSlave()
                warning_log = "MySQL> %s" % ret
                log_obj.warn("MySQL> %s" % ret)
                mail_content = mail_content +"\n" + warning_log
                send_mail(sub, mail_content, to_list, mail_host, mail_user, mail_pass, mail_postfix) 

            except Exception, err:

                log_obj.warn(string(err))
    
    except Exception, err:

        log_obj.error("\nCreate connection failed,mysql cannot connected.....")
    		
        db.disconnect()
    
