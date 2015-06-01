# -*- coding: utf-8 -*-

import re
import subprocess
import threading


def get_ip():
    try:
        import netifaces
    except ImportError:
        __NETIFACES_IMPORTED = False
    else:
        __NETIFACES_IMPORTED = True

    if __NETIFACES_IMPORTED:
        for iface in netifaces.interfaces():
            if iface.startswith('eth'):
                return netifaces.ifaddresses(iface)[netifaces.AF_INET][0] \
                        ['addr']
    else:
        p = subprocess.Popen(['ip', '-4', '-o', 'addr', 'show'],
                stdout=subprocess.PIPE)
        for l in p.communicate()[0].split('\n'):
            if not ': eth' in l:
                continue
            m = re.search(r'inet (([0-9]{1,3}\.){3}[0-9]{1,3})', l)
            try:
                return m.group(1)
            except:
                return '0.0.0.0'
        else:
            return '0.0.0.0'


class Lcm(object):
    def __init__(self):
        self.__lock = threading.RLock()
        self._BUS = '2'
        self._ADDR = '0x20'
        self._WIDTH = 0x10
        self._HEIGHT = 0x2
        self._HIDDEN_WIDTH_BOUNDARY = 40
        self._messages = ('', '')
        try:
            import smbus
        except ImportError:
            self.__SMBUS_IMPORTED = False
        else:
            self.__SMBUS_IMPORTED = True
            self._bus = smbus.SMbus(self._BUS)
        self.init()

    def refresh(self):
        with self.__lock:
            self.clear()
            for line in self.messages:
                for i in [str(ord(c)) for c in line \
                        + ' ' * (self._HIDDEN_WIDTH_BOUNDARY - len(line))]:
                    self.write(i)

    def init(self):
        with self.__lock:
            self.write('0x1B')
            self.write('0x40')

    def clear(self):
        with self.__lock:
            self.write('0x0C')

    def write(self, value):
        if self.__SMBUS_IMPORTED:
            self._bus.write_byte(self._ADDR, value)
        else:
            subprocess.call(['i2cset', '-y', self._BUS, self._ADDR, value])

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, msg):
        if not hasattr(msg, '__iter__'):
            raise TypeError('messages is not iterable')
        if len(msg) > self._HEIGHT:
            raise IndexError('too many messages')
        self._messages = msg


def get_lcm():
    return lcm


lcm = Lcm()


__version__ = '1.0'
__all__ = (
    'get_lcm',
    'get_ip',
    'Lcm',
)
