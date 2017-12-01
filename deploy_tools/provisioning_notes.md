## Required packages:
* nginx
* Python 3.6
* virtualenv + pip
* Git

eg, on ubuntu:
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get install nginx git python3.6 python3.6-venv

## Nginx Virtual Host config
* see nginx.template.conf
* replace SITENAME with, e.g., stanging.my-domain.com

## Systemd service 

* see gunicorn-systemd.template.service
* replace SITENAME with, e.g., staging.my-domain.com

## Folder structure:
Assume we have a user account at /home/username
