#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time

from datetime import timedelta
from temperusb.temper import TemperHandler

# joel, kjell, ingrid, marte, anne, sindre
WHITELIST = ['4797954918', '4799593407', '4790635772', '4798044603', '4741488696', '4795428924']  # always start with country code, excluding +
PLUGS = {'1': {'on': 10737676, 'off': 10737668},
         '2': {'on': 10737674, 'off': 10737666},
         '3': {'on': 10737673, 'off': 10737665},
         '4': {'on': 10737677, 'off': 10737669},
         '5': {'on': 10737675, 'off': 10737667}}
ROOT_PATH = os.path.dirname(sys.argv[0])


class SmsHandler(object):
    def send(self, number, message, path='/var/spool/sms/outgoing'):
        with open(os.path.join(path, 'sms'), 'w') as f:
            f.write('To: {0}\n\n{1}'.format(number, message))
    
    def receive(self, messagefile):
        with open(messagefile, 'r') as f:
            sender = f.readline().split(' ')[1].rstrip()
            text = f.readlines()[-1]

        return sender, text


class TempHandler(object):
    def __init__(self):
        self.handle = TemperHandler()

    def fetch(self):
        for device in self.handle.get_devices():
            try:
                temp = device.get_temperature()
            except Exception:
                temp = 'U'

            return temp - 10  # junk termostat, need to correct the temperature accordingly


class RFHandler(object):
    def __init__(self):
        self.repeat = 3
        self.channel = 1
        self.pulselength = 171

    def send(self, code):
        for i in range(self.repeat):
            os.system('{0} {1} {2} {3} > /dev/null 2>&1'.format(os.path.join(ROOT_PATH, 'codesend'), 
                                                                code, 
                                                                self.channel, 
                                                                self.pulselength))
        time.sleep(1.5)


class UptimeHandler(object):
    def uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            td = timedelta(seconds = uptime_seconds)
            days, hours, minutes = td.days, td.seconds // 3600, td.seconds // 60 % 60
            return '{0} dager, {1} timer, {2} minutter'.format(days, hours, minutes)


class Main(object):
    def __init__(self):
        self.t = TempHandler()
        self.s = SmsHandler()
        self.r = RFHandler()
        self.u = UptimeHandler()

        self.storageFile = os.path.join(ROOT_PATH, "active.txt")

    def status(self, recipient, send=False):
        active = self.fetch_active_plugs()
        msg = ''
        temp = 'Temperaturen er {0:.1f} grader.'.format(self.t.fetch())

        if not active:
            msg = 'Ingen kontakt er aktiv.'
        else:
            msg = 'Kontakt {0} er aktiv.'.format(' '.join(sorted(active)))

        if send:  # only send reply when function is directly called
            return self.s.send(recipient, '{0} {1}'.format(msg, temp))

        return '{0} {1}'.format(msg, temp)

    def start(self, recipient, plugs):
        active = self.fetch_active_plugs()
        msg = ''
        added = []

        for plug in plugs:
            if plug not in active and plug.isdigit():
#                print('Powering on plug {}'.format(plug))
                self.r.send(PLUGS[str(plug)]['on'])
                added.append(plug)
                active.append(plug)

        self.write_active_plugs(active)

        if added:
            msg = 'Kontakt {0} er nå aktivert. '.format(' '.join(sorted(added)))

        msg += '{0}'.format(self.status(recipient))

        return self.s.send(recipient, msg)

    def stop(self, recipient, plugs):
        active = self.fetch_active_plugs()
        msg = ''
        stopped = []

        for plug in plugs:
            if plug in active and plug.isdigit():
#                print('Powering off plug {}'.format(plug))
                self.r.send(PLUGS[str(plug)]['off'])
                stopped.append(plug)
                active.remove(plug)

        self.write_active_plugs(active)

        if stopped:
            msg = 'Kontakt {0} er nå deaktivert. '.format(' '.join(sorted(stopped)))

        msg += '{0}'.format(self.status(recipient))

        return self.s.send(recipient, msg)

    def uptime(self, recipient):
        msg = "Oppetid er {}.".format(self.u.uptime())

        return self.s.send(recipient, msg)

    def fetch_active_plugs(self):
        plugs = []

        with open(self.storageFile, 'r') as f:
            plugs = f.read()

        if not plugs:
            return []

        return plugs.split(',')

    def write_active_plugs(self, plugs):
        with open(self.storageFile, 'w+') as f:
            f.write(','.join(plugs))

    def run(self, messagefile):

        number, message = self.s.receive(messagefile)

        if number not in WHITELIST:
            return
        message = message.split(' ')

        keyword = message[0].lower()
        plugs = []

        if len(message[1:]) == 1: # start 123
            for i in message[1]:
                plugs.append(i)
        else: # start 1 2 3
            plugs = message[1:]

        if keyword == 'status':
            return self.status(number, send=True)

        if keyword == 'start':
            return self.start(number, plugs)

        if keyword == 'stop':
            return self.stop(number, plugs)

        if keyword == 'uptime':
            return self.uptime(number)

if __name__ == '__main__':
    if sys.argv[1].lower() == 'received':
        m = Main()
        m.run(sys.argv[2])
