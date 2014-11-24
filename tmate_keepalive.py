#!/usr/bin/env python
"""This daemon checks for a tmate socket and connection and if there
is none it creates one and then emails the credentials to the Administrators
"""
import sys
import time
import subprocess
from daemon import Daemon

import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.Utils import COMMASPACE
from email.MIMEBase import MIMEBase
from email.parser import Parser
from email.MIMEImage import MIMEImage
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
import mimetypes


def email(ssh):
    SERVER = "smtp.gmail.com"
    PORT = 587
    PASSWD = "kaurhxvutmuvqbic"
    server = smtplib.SMTP()
    server.connect(SERVER, PORT)
    server.ehlo()
    server.starttls()
    server.login('cestdiego@gmail.com', PASSWD)

    fromaddr = "cestdiego@gmail.com"
    tolist = ["cestdiego@gmail.com"
              , "ce.cruz@gmail.com"]

    sub = "New tmate session was created"
    body = "Hi, it seems your tmate session has been closed.\n\nDon't worry, you can access the new one with:\n " + ssh

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = COMMASPACE.join(tolist)
    msg['Subject'] = sub
    msg.attach(MIMEText(body))
    msg.attach(MIMEText('\nSent from your Pi Cluster at the UNI', 'plain'))

    server.sendmail(fromaddr, tolist, msg.as_string())


class tmateDaemon(Daemon):
    def run(self):
        tmate_get_ssh = "tmate -S /tmp/tmate.sock display -p '#{tmate_ssh}'"
        tmate_new_session = "cd && tmate -S /tmp/tmate.sock new-session -d"
        while True:
            if (subprocess.call(tmate_get_ssh, shell=True)):

                subprocess.call(tmate_new_session, shell=True)
                time.sleep(3)
                ssh = subprocess.check_output(tmate_get_ssh,
                                              stderr=subprocess.STDOUT,
                                              shell=True)
                email(ssh)
            else:
                ssh = subprocess.check_output(tmate_get_ssh,
                                              stderr=subprocess.STDOUT,
                                              shell=True)
                if(subprocess.call(ssh, shell=True)):
                    subprocess.call(tmate_new_session, shell=True)
                    time.sleep(3)
                    ssh = subprocess.check_output(tmate_get_ssh,
                                                  stderr=subprocess.STDOUT,
                                                  shell=True)
                    email(ssh)



            time.sleep(1)


if __name__ == "__main__":
    daemon = tmateDaemon('/tmp/tmate_keepalive.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            sys.stdout.write("Unknown command\n")
            sys.exit(2)
        sys.exit(0)
    else:
        sys.stdout.write("Usage: %s start|stop|restart|status\n" % sys.argv[0])
        sys.exit(2)
