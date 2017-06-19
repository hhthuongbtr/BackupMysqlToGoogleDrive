#!/bin/bash
name="monitor-$(date +"%Y-%m-%d").sql"
cd /script/BackupMysqlToGoogleDrive && mysqldump -u mysqlbackup -p11nit0rA93nt monitor -h 10.0.21.32 > $name && /usr/bin/python push_google_drive.py $name > /dev/null && /bin/rm -rf $name
