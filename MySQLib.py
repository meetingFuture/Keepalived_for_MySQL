#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: hailong.sun1982@gmail.com  at 2017.05

import logging, logging.handlers  
import MySQLdb
import smtplib
import sys
import commands
import time
from email.mime.text import MIMEText 

class MySQLBase(object):


    def __init__(self, DB_HOST='192.168.11.123', DB_PORT=3306, DB_USER='xxxx', DB_PWD='1111', DB_NAME='mysql'):
            self.DB_HOST = DB_HOST 
            self.DB_PORT = DB_PORT
            self.DB_USER = DB_USER
            self.DB_PWD = DB_PWD
            self.DB_NAME = DB_NAME
            self.conn = self.getConnection()

    def getConnection(self):
            return MySQLdb.Connect( 
                host=self.DB_HOST, 
                port=self.DB_PORT, 
                user=self.DB_USER,
                passwd=self.DB_PWD, 
                db=self.DB_NAME,
                charset='utf8'
                )

    def query(self, sql):
            try:
                cursor=self.conn.cursor() 
                cursor.execute(sql) 
                returnData=cursor.fetchall() 
                cursor.close() 
                return returnData
            except Exception, err:
                return err

    def queryDict(self, sql):
            try:
                cursor=self.conn.cursor(MySQLdb.cursors.DictCursor) 
                cursor.execute(sql) 
                returnData=cursor.fetchall() 
                cursor.close() 
                return returnData
            except Exception, err:
                return err     

    def queryone(self, sql):
            try:
                cursor=self.conn.cursor()
                cursor.execute(sql)
                returnData=cursor.fetchone()
                cursor.close()
                return returnData
            except Exception, err:
                return err

    def update(self, sql): 
            try:
                cursor=self.conn.cursor() 
                cursor.execute(sql) 
                self.conn.commit() 
                cursor.close() 
            except Exception, err:
                return err

    def delete(self, sql):
            try:
                cursor=self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()
                cursor.close()
            except Exception, err:
                return err

    def insert(self,sql):
            try:
                cursor = self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()
            except Exception, err:
                return err

    def commitTransaction(self):
            self.conn.commit()

    def closeCursor(self):
            cursor = self.conn.cursor()
            cursor.close()

    def lastinsertid(self):
            cursor = self.conn.cursor()
            cursor.execute("select LAST_INSERT_ID()")
            data = cursor.fetchone()
            cursor.close()
            return data

class SwitchHandler(MySQLBase):



    def __init__(self, DB_HOST='192.168.11.123', DB_PORT=3306, DB_USER='xxxx', DB_PWD='1111', DB_NAME='mysql'):
        super(SwitchHandler, self).__init__(DB_HOST = DB_HOST, DB_PORT=DB_PORT, DB_USER=DB_USER, DB_PWD=DB_PWD, DB_NAME=DB_NAME)

    def __setParams(self, _input_sql):

            cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            input_sql = _input_sql
            if  input_sql.strip() != '' :
                try:
                    cursor.update(input_sql)
                    return True
                except Exception, err:
                    return err

    def switchTomaster(self, switchsql):
        """
        switch to master!
        """
        sql = switchsql
        # print sql
        ret = self.update(sql)
        return ret
    
    def run_mysql_cmd(self, _input_sql):
        """
        switch to master!
        """
        return self.__setParams(_input_sql)

    def __get_slave_status_param(self, _queyr_item):
        """
        Get slave parameter according input
        """

        slave_status_sql = """show slave status"""
        slave_status_tuple = self.queryDict(slave_status_sql)
        slave_status_dict = slave_status_tuple[0]
        try:
            slave_status_value = slave_status_dict[_queyr_item]
        except KeyError:
            return NONE
        return slave_status_value.encode("utf-8")

    def get_slave_status(self, _queyr_item):
        """
        Get slave status
        """

        slave_status_sql = """show slave status"""
        slave_status_tuple = self.queryDict(slave_status_sql)
        slave_status_dict = slave_status_tuple[0]
        return slave_status_dict

    def get_master_host(self): 
        """
        Slave is delayed!
        """

        old_master_host  = self.__get_slave_status_param("Master_Host")
        return old_master_host

    def parse_gtid(self, gtid_str):
        sever_uuid_str = gtid_str.split(':')[0]
        range_seq = gtid_str.split(':')[1].split('-')[-1]
        return sever_uuid_str, range_seq

    def slave_is_delay(self): 
        """
        Slave is delayed!
        """
        
        Retrieved_Gtid_Set_str = self.__get_slave_status_param("Retrieved_Gtid_Set")
        ret_server_uuid, ret_range_seq = self.parse_gtid(Retrieved_Gtid_Set_str)
        Retrieved_Gtid_Set_list = [ret_server_uuid, ret_range_seq]

        Executed_Gtid_Set_raw_list = self.__get_slave_status_param("Executed_Gtid_Set").split(',\n')
        Executed_Gtid_Set_list = []
        for gtidline in Executed_Gtid_Set_raw_list:
            #print gtidline
            _server_uuid, _range_seq = self.parse_gtid(gtidline)
            Executed_Gtid_Set_list.append([_server_uuid, _range_seq])
            #print Executed_Gtid_Set_list
        
        if Retrieved_Gtid_Set_list in Executed_Gtid_Set_list:
            return True
        else:
            return False

    def get_master_gtid(self):
        """
        Get master gtid
        """
        master_gtid = self.__get_slave_status_param("Master_UUID")
        return master_gtid

    def get_slave_exec_set(self): 
        """
        Get slave execute gtid!
        """
        # 输出：['2c40ecea-0a4e-11e7-abbd-000c296d47cb:1-5', '32467c23-0a49-11e7-8cf5-000c29fe0453:1-2']
        Executed_Gtid_Set_list = self.__get_slave_status_param("Executed_Gtid_Set").split(',\n')
        return sorted(Executed_Gtid_Set_list)

    def get_slave_exec_gtid(self): 
        """
        Get slave execute gtid!
        """
        # 输出：['2c40ecea-0a4e-11e7-abbd-000c296d47cb:1-5', '32467c23-0a49-11e7-8cf5-000c29fe0453:1-2']
        Executed_Gtid_Set_list = self.__get_slave_status_param("Executed_Gtid_Set").split(',\n')
        #print self.DB_HOST, Executed_Gtid_Set_list
        master_gtid = self.get_master_gtid()
        #print "master_gtid:" + master_gtid
        # 输出 ['2c40ecea-0a4e-11e7-abbd-000c296d47cb:1']
        exec_gtid_list = [ l for l in Executed_Gtid_Set_list if l.startswith(master_gtid)]
        # print "exec_gtid_list:" + exec_gtid_list
        # '2c40ecea-0a4e-11e7-abbd-000c296d47cb:1-5',  1-5
        #print exec_gtid_list
        exec_gtid_str = exec_gtid_list[0].split(':')[-1]
        # 
        exec_seq = exec_gtid_str.split('-')[-1]

        #print master_gtid, exec_gtid_list, exec_gtid_str, exec_seq
        return exec_seq

            
    def slave_thread_is_running(self): 
        """
        Slave thread is running!
        """

        Slave_IO_Running_value = self.__get_slave_status_param("Slave_IO_Running")
        Slave_SQL_Running_value = self.__get_slave_status_param("Slave_SQL_Running")
        if Slave_IO_Running_value == 'Yes' and Slave_SQL_Running_value =='Yes':
            return True
        else:
            return False


class LogMgr:  


    def __init__ (self, logpath):  

        self.LOG = logging.getLogger('log')  
        loghdlr = logging.handlers.TimedRotatingFileHandler(filename=logpath, when="M", interval=1, backupCount=2)  
        fmt1 = logging.Formatter("%(asctime)s %(threadName)-10s %(message)s", "%Y-%m-%d %H:%M:%S")  
        loghdlr.setFormatter(fmt1)  
        self.LOG.addHandler(loghdlr)  
        self.LOG.setLevel(logging.INFO)  
  

    def note(self, msg):  

        if self.LOG is not None:  
            self.LOG.NOTSET(msg)  

    def info(self, msg):  

        if self.LOG is not None:  
            self.LOG.info(msg)  

    def warn(self, msg):  

        if self.LOG is not None:  
            self.LOG.warn(msg)  

    def error(self, msg):  

        if self.LOG is not None:  
            self.LOG.error(msg)  

    def crit(self, msg):  

        if self.LOG is not None:  
            self.LOG.CRITICAL(msg)  

    def debug(self, msg):  

        if self.LOG is not None:  
            self.LOG.debug(msg)  



#发送邮件
def send_mail(sub, content, to_list, mail_host, mail_user, mail_pass, mail_postfix):  

    _mail_host, _mail_user, _mail_pass = mail_host, mail_user, mail_pass
    print _mail_host, _mail_user, _mail_pass
    _mail_postfix = mail_postfix

    me="keepalived_monitor"+"<"+_mail_user+"@"+_mail_postfix+">"  
    msg = MIMEText(content,_subtype='html',_charset='gb2312')
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  

    try:  

        server = smtplib.SMTP()  
        server.connect(_mail_host)  
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(_mail_user,_mail_pass)  
        server.sendmail(me, to_list, msg.as_string())  
        server.close()  
        print "mail sended"
        return True  

    except Exception, e:  
        print str(e)  
        return False

def run_cmd(cmd):
    import subprocess
    ret_out=''
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        ret_out = p.stdout.read().strip()
        ret_code = p.returncode
        if p.stderr:
            ret_err = p.stderr.read().replace("\n", " ")
        else:
            ret_err = ""
        return ret_code, ret_err, ret_out

    except Exception, err:
        return None, err, None

def send_sms( content, mobile_list ):

    _mobile_list = ",".join([ str(line) for line in mobile_list ])
    _content = content.strip()

    send_cmd_str = """curl -d "content=%s&tos=%s," "http://192.168.121.21:3232/sms" """ %( _content, _mobile_list)
    #print send_cmd_str
    ret = run_cmd( send_cmd_str ) 
    return ret
