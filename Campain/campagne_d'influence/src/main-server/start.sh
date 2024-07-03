#!/bin/bash
/usr/sbin/sshd -D &

/usr/local/bin/init-script.sh
node app.js
