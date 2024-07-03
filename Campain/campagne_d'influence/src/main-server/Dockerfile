FROM node:14

RUN apt-get update && apt-get install -y openssh-server

RUN mkdir /var/run/sshd

RUN echo 'root:Z~rd.%Y977xpukG_F=-LD8i4P98' | chpasswd  

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd

RUN echo 'ECTF{b3w4r3_0f_p4ss1ng_tr41n}' > /root/flag.txt
RUN echo "#this may be uselful for something ',:) 98869945 " > /root/secret_code.txt

EXPOSE 22 3000

WORKDIR /usr/src/app

COPY app/package*.json ./
RUN npm install 
RUN npm i express-fileupload

COPY app/ ./

COPY init-script.sh /usr/local/bin/init-script.sh
RUN chmod +x /usr/local/bin/init-script.sh

COPY start.sh /usr/src/app/start.sh
CMD ["/bin/bash", "/usr/src/app/start.sh"]
