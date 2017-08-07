# Keepalived_for_MySQL
Keepalived for MySQL
Version: 1.0

Howto: 
1. You need to define the config.py which is the config of the check scripts
2. And set your sms url of the function send_sms in MySQLib.py 

Instruction: 

MySQLib.py:  The project library with the connection\Logging\Email\Sms Funcs.
checkMySQL.py: Keepalived check alived script which will check MySQL instance health and gatway is alive.
notify.py: When Keepalived switch to master or backup or fail state, the script will be executed.
config.py: The project's config file.

Email: hailong.sun1982@gmail.com 
QQ: 173386747