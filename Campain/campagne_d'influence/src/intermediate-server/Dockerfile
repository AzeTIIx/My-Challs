#Intermediate server
FROM node:14

#Install any additional system dependencies
RUN apt-get update && apt-get install -y cron curl openssh-server sudo netcat iputils-ping

RUN useradd -m appuser

RUN echo 'appuser ALL=(root) NOPASSWD: /scripts/run.sh' > /etc/sudoers.d/appuser
RUN chmod 0440 /etc/sudoers.d/appuser

COPY app/ /app/
COPY run.sh /scripts/run.sh
COPY f.sh /scripts/f.sh
COPY ssh_config /etc/ssh/ssh_config
WORKDIR /app
RUN chmod 766 /scripts/f.sh
RUN chmod 744 /scripts/run.sh
RUN rm -f /app/run.sh
RUN rm -f /app/f.sh
RUN npm install 
RUN npm i express-fileupload

#SSH config
RUN mkdir /var/run/sshd
RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -N ""

USER appuser

CMD ["sh", "-c", "sudo /usr/sbin/sshd -D & sleep 5 && sudo /scripts/run.sh && node /app/app.js"]
