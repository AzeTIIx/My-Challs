#!/bin/bash
while [ ! -f /remote-ssh-keys/id_rsa.pub ]
do
  sleep 1
done
mkdir -p ~/.ssh
cp /remote-ssh-keys/id_rsa.pub ~/.ssh/authorized_keys
while true; do sleep 1000; done
