#!/usr/bin/bash
name="monitor-$(date +"%Y-%m-%d").sql"
mysqldump -u root -proot monitor > $name && /usr/bin/python ./test.py $name > /dev/null && /bin/rm -rf $name