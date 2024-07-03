#!/bin/bash

MEDIA_DIR="/app/tempmedia"
mkdir -p ${MEDIA_DIR}

MAIN_SERVER="root@main-server" 
REMOTE_MEDIA_PATH="/usr/src/app/media/*"  

SSH_KEY="/root/.ssh/id_rsa"

scp -i ${SSH_KEY} -P 22 -o StrictHostKeyChecking=no ${MAIN_SERVER}:${REMOTE_MEDIA_PATH} ${MEDIA_DIR}/
