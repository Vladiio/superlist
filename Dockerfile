FROM 'jenkinsci/blueocean'

USER root

RUN echo "http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
 	echo "http://nl.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
 	echo "http://nl.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories

RUN apk update && apk upgrade && apk add python3 python3-dev gcc firefox xvfb dbus npm

RUN export DISPLAY=:0.0

WORKDIR /var/jenkins_home/

RUN wget \
 https://github.com/mozilla/geckodriver/releases/download/v0.21.0/geckodriver-v0.21.0-linux64.tar.gz \
 && tar -xvf geckodriver-v0.21.0-linux64.tar.gz \
 && mv geckodriver /usr/local/bin

RUN wget \
 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 \
 && tar -xvf phantomjs-2.1.1-linux-x86_64.tar.bz2 \
 && mv phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin
