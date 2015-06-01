#! /usr/bin/python

import time
import json
import base64
import httplib
import sys
import os
import os.path
import binascii
import subprocess
from crypt import crypt
import rdf022
import Queue
from serial import Serial
from threading import Thread, Event
from config import ArgsConfig, AsicConfig
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.serialport import SerialPort
from twisted.protocols.basic import LineReceiver
import binascii
import socket
import requests
from requests.auth import HTTPBasicAuth

class WebUIProtocol(WebSocketServerProtocol):
    def __init__(self):
        self.command_option = {'version': self.web_version, \
                               'login': self.web_login, \
                               'control': self.web_control, \
                               'hashrate': self.web_hashrate, \
                               'pool_config': self.web_pool_config, \
                               'host_config': self.web_host_config, \
                               'access_ctrl': self.web_access_ctrl, \
                               'upgrade': self.web_upgrade, \
                               'diag_report': self.web_diag_report, \
                               'clean_job': self.clean_job
                              }
        self.stratum_proxy = None

    def onConnect(self, request):
        print 'Connecting...'

    def onOpen(self):
        if (self.transport.getPeer().host != '127.0.0.1'):
            ws_client.append(self)
        print 'Opening...[%s]' % self.transport.getPeer().host

    def onClose(self, wasClean, code, reason):
        try:
            ws_client.remove(self)
        except ValueError:
            pass
        print 'Close...[%s]' % self.transport.getPeer().host

    def onMessage(self, data, isBinary):
        #if (data == 'hashrate'):
        #    self.sendMessage(json.dumps(global_khrate), isBinary=False)
        try:
            web_req = json.loads(data)
            if (web_req == None):
                print 'Unrecognized command!'
            mtd = web_req['method']
            self.command_option[mtd](web_req)
        except Exception, e:
            #print e
            print data
            rsp = {'result':False, 'error':'command error!' + str(e), 'id':'0'}
            print json.dumps(rsp)
            self.sendMessage(json.dumps(rsp))
            return False

    def web_version(self, req):
        ws_client.append(self)
        rsp = {'result':False, 'error':None, 'id':None}
        rsp['id'] = req['id']
        rsp['result'] = VERSION
        self.sendMessage(json.dumps(rsp))

        return

    def web_login(self, req):
        rsp = {'result':False, 'error':None, 'id':None}
        pwd = req['params'][0]
        rsp['id'] = req['id']

        f = open('access_code', 'r')
        crypted_pwd = f.readline().rstrip()
        f.close()
        #print '(%s)(%s)' % (pwd, crypted_pwd)
        if (crypt(pwd, crypted_pwd) == crypted_pwd):
            rsp['result'] = True
        else:
            rsp['result'] = False

        self.sendMessage(json.dumps(rsp))

        return

    def web_control(self, req):
        print 'control...'
        if (req['params'][0] == 'go'):
            config.read_config()
            print '>start...'
            if (config.protocol == 'stratum+tcp:'):
                stratum_host = config.host
                stratum_port = config.port
                config.host = 'localhost'
                config.port = '8332'
                # startup stratum mining proxy
                print '>startup stratum proxy...'
                stratum_proxy.start(stratum_host, stratum_port, config.port, config.username, config.password)
                time.sleep(3)
            # startup miner threads...
            miner_ctrl.set()
        else:
            # stop all miner thread
            miner_ctrl.clear()
            stat_reset.set()
            # set all board to be idle
            for b in sorted(brd):
                brd[b].set_all_idle()
            try:
                print '>stop stratum proxy...'
                stratum_proxy.stop()
            except OSError:
                pass
        return

    def web_hashrate(self, req):
        print 'report_hashrate...'
        rsp = {'result':False, 'error':None, 'id':None}
        rsp['result'] = json.dumps(global_khrate)
        rsp['id'] = req['id']
        self.sendMessage(json.dumps(rsp))
        return

    def web_pool_config(self, req):
        rsp = {'result':False, 'error':None, 'id':None}

        if len(req['params']) == 0:
            config.read_config()
            rsp['result'] = [config.protocol, config.host, config.port, config.username, config.password]
            rsp['error'] = None
            rsp['id'] = req['id']
            self.sendMessage(json.dumps(rsp))
        else:
            (protocol, host, port, username, password) = (i for i in req['params'])
            (config.protocol, config.host, config.port, config.username, config.password) = (protocol, host, port, username, password)
            cr = config.save_config()
            if (cr):
                rsp['result'] = ["ok"]
                rsp['error'] = None
                rsp['id'] = req['id']
                self.sendMessage(json.dumps(rsp))
                # Inform all thread to change pool information
                for p in pool_ctrl:
                    pool_ctrl[p].set()
                submitter_ctrl.set()

                # stop all miner thread
                miner_ctrl.clear()
                stat_reset.set()
                # set all board to be idle
                for b in sorted(brd):
                    brd[b].set_all_idle()
                try:
                    print '>stop stratum proxy...'
                    stratum_proxy.stop()
                except OSError:
                    pass

                time.sleep(1)

                # start all miner thread
                if (config.protocol == 'stratum+tcp:'):
                    stratum_host = config.host
                    stratum_port = config.port
                    config.host = 'localhost'
                    config.port = '8332'
                    # startup stratum mining proxy
                    print '>startup stratum proxy...'
                    stratum_proxy.start(stratum_host, stratum_port, config.port, config.username, config.password)
                    time.sleep(3)
                # startup minter threads...
                miner_ctrl.set()

    def web_host_config(self, req):
        rsp = {'result':False, 'error':None, 'id':None}

        if len(req['params']) == 0:
            f = open('/etc/network/interfaces', 'r')
            fif = f.readlines()
            f.close()
            binding = ''
            ipaddr = ''
            netmask = ''
            gateway = ''
            dns = ''
            fixed = False
            for i in fif:
                a = '' if i.lstrip().startswith('#') else i
                if ('dhcp' in a) and ('eth1' in a):
                    binding = 'dhcpc'
                    break
                if ('static' in a) and ('eth1' in a):
                    binding = 'fixedip'
                    fixed = True
                    continue
                if fixed:
                    aa = a.split()
                    for j in range(len(aa)):
                        if 'address' in aa[j]:
                            ipaddr = aa[j+1]
                        if 'netmask' in aa[j]:
                            netmask = aa[j+1]
                        if 'gateway' in aa[j]:
                            gateway = aa[j+1]
                        if 'dns-nameservers' in aa[j]:
                            dns = aa[j+1]
            rsp['result'] = [binding, ipaddr, netmask, gateway, dns]
            rsp['error'] = None
            rsp['id'] = req['id']
            self.sendMessage(json.dumps(rsp))
        else:
            (binding, ipaddr, netmask, gateway, dns) = (i for i in req['params'])
            f = open('/etc/network/interfaces', 'w+')
            f.write('# loopback network interface\n')
            f.write('auto lo\n')
            f.write('iface lo inet loopback\n\n')
            f.write('# primary network interface\n')
            f.write('auto eth1\n')
            if (binding == 'dhcpc'):
                f.write('iface eth1 inet dhcp\n')
            else:
                f.write('iface eth1 inet static\n')
                f.write('address ' + ipaddr + '\n')
                f.write('netmask ' + netmask + '\n')
                f.write('gateway ' + gateway + '\n')
                f.write('dns-nameservers ' + dns + '\n')
            f.close()

            rsp['result'] = ["ok"]
            rsp['error'] = None
            rsp['id'] = req['id']
            self.sendMessage(json.dumps(rsp))

            #subprocess.call(['sh', 'network_restart'], shell=False)
            time.sleep(0.5)
            subprocess.call(['/sbin/ifdown', 'eth1'], shell=False)
            time.sleep(0.5)
            subprocess.call(['/sbin/ifup', 'eth1'], shell=False)

    def web_access_ctrl(self, req):
        rsp = {'result':False, 'error':None, 'id':None}
        print 'access_ctrl...'
        (old_password, new_password) = (req['params'][0], req['params'][1])
        f = open('access_code', 'r')
        crypted_pwd = f.readline().rstrip()
        f.close()
        if (crypt(old_password, crypted_pwd) == crypted_pwd):
            f = open('access_code', 'w')
            new_crypt = crypt(new_password, 'TomSoong')
            f.write(new_crypt + '\n')
            f.close()
            rsp['result'] = ['ok']
        else:
            rsp['result'] = ['wrong']
        rsp['id'] = req['id']
        self.sendMessage(json.dumps(rsp))

        return

    def web_upgrade(self, req):
        print 'upgrade...'
        return

    def web_diag_report(self, req):
        class DiagThread(Thread):
            def __init__(self, protocol):
                Thread.__init__(self)
                self.protocol = protocol
            def diag_report_str(self, s):
                rsp = {'result':s, 'error':None, 'id':'d0'}
                reactor.callFromThread(self.protocol.sendMessage, json.dumps(rsp))
            def diag_report_brd(self, bid, r):
                rsp = {'result':r, 'error':None, 'id':'d_'+bid}
                reactor.callFromThread(self.protocol.sendMessage, json.dumps(rsp))
            def run(self):
                self.diag_report_str('Start scanning...')
                for b in sorted(brd):
                    self.diag_report_str('Scanning board ' + b + '...')
                    brd[b].calc_asic_cores(scan=False)
                    self.diag_report_brd(b, brd[b].asic)
                self.diag_report_str('Scan complete!')   
        DiagThread(self).start()

    def clean_job(self, req):
        print 'clean job!'
        # put 9-byte 'FF' to inform all board to clean jobs immediately
        for bid in ans_queue:
            ans_queue[bid].put('ffffffffffffffffff')
        return

class StratumProxy(object):
    def __init__(self):
        self.proxy = None
        self.isRunning = False

    def start(self, stratum_host, stratum_port, getwork_port, username, password):
        if not self.isRunning:
            self.proxy = subprocess.Popen(['/usr/bin/python', 'stratum-mining-proxy/mining_proxy.py', \
                                            '-o', stratum_host, '-p', stratum_port, '-gp', getwork_port , \
                                            '-cu', username, '-cp', password, '-pa', 'scrypt', \
                                            '-nm', '-q'], stdout=subprocess.PIPE, shell=False)
            self.isRunning = True

    def stop(self):
        if self.isRunning:
            self.proxy.kill()
            os.wait()
            self.isRunning = False

if __name__ == '__main__':


    stratum_proxy = StratumProxy()

    factory = WebSocketServerFactory('ws://127.0.0.1:9000', debug=True)
    factory.protocol = WebUIProtocol
    reactor.listenTCP(9000, factory)

    print 'Reading config.ini...'
    if os.path.isfile('config.ini'):
        config = ArgsConfig('config.ini')
        config.read_config()
    else:
        print 'config.ini does exist!'
        sys.exit()

    if (config.protocol == 'stratum+tcp:'):
        stratum_host = config.host
        stratum_port = config.port
        config.host = 'localhost'
        config.port = '8332'

    if (config.immediately_run == 'yes'):
        print 'immediately_run...'
        if (config.protocol == 'stratum+tcp:'):
            # startup stratum mining proxy
            print '>startup stratum proxy...'
            stratum_proxy.start(stratum_host, stratum_port, config.port, config.username, config.password)

    time.sleep(8)

    reactor.run()

