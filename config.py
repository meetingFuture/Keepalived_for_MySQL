#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: hailong.sun1982@gmail.com  at 2017.05

lockfile="/tmp/.keepalived_notify.lock"
# MySQL_Version values is "5.6" or "5.7"
MySQL_Version="5.7"
# MySQL host public IP Address
dbhost='192.168.1.9'
# MySQL port
dbport = 3306
# MySQL user with super privilege
dbuser = 'user'
dbpassword='password'
# slave hostname sufix
# slave_suffix=['01']
# Execute command when change to  slave 
slave_task="stop slave; set global innodb_flush_log_at_trx_commit=0;set global sync_binlog=0; set global read_only=1;start slave;"
# Execute command when change to  master 
master_task="set global innodb_flush_log_at_trx_commit=1;set global sync_binlog=1; set global read_only=0;stop slave;"
sms_list = [
13600136000,
]
mailto_list = [
'hailong.sun1992@gmail.com',
]
mail_host="mail.google.com" 
mail_user="monitor@google.com" 
mail_pass="google.com" 
mail_postfix="google.com" 
sub="Critical: Keepalived switched"
