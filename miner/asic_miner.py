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

VERSION = '1.1.4'

#------- hw.py --------
#from serial import Serial
#import subprocess
#from time import sleep
#import binascii

MAX_BOARDS = 8
MAX_CHIPS = 32
MAX_CLUSTERS = 6
MAX_CORES = 9

g_tail = '00000000000000000000000000000000a78e0100000001000000f615f7ce3b4fc6b8f61e8f89aedb1d0852507650533a9e3b10b9bbcc30639f279fcaa86746e1ef52d3edb3c4ad8259920d509bd073605c9bf1d59983752a6b06b817bb4ea78e011d012d59d4'

class AsicBoard(object):

    def __init__(self, com_port, reset_gpio, prt):
        self.comport_mode = 0               # comport_mode: 0 for synchronous, 1 for asynchronous
        self.com_port = com_port
        self.reset_gpio = reset_gpio
        self.prt = prt
        self.asic = \
        {
            '00': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '01': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '02': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '03': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '04': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '05': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '06': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '07': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '08': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '09': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '0a': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '0b': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '0c': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '0d': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '0e': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '0f': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '10': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '11': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '12': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '13': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '14': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '15': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '16': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '17': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '18': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '19': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '1a': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '1b': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '1c': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '1d': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '1e': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000},
            '1f': {'00':0x0000, '01':0x0000, '02':0x0000, '03':0x0000, '04':0x0000, '05':0x0000}
        }
        self.good_cores = 0
        self.bad_cores = 0

    def set_comport_sync_mode(self):
        self.comport_mode = 0

    def set_comport_async_mode(self):
        self.comport_mode = 1

    def write_by_hex(self, data):
        if (self.comport_mode == 0):
            self.com_port.write(data.decode('hex')[::-1])
        else:
            reactor.callFromThread(AlcheProtocol.sendLine, self.prt, data.decode('hex')[::-1])

    def reset(self):
        return subprocess.call(['sh', 'reset_board', self.reset_gpio], shell=False)

    def flush(self, count):
        resp = self.com_port.read(count)               # max 10 bytes x 32 chips x 6 cluster = 1920 bytes
        while len(resp) > 0:
            resp = self.com_port.read(count)

    # setup all asics to run on PLL @ 360Mhz
    def set_pll(self):
        for chp in sorted(self.asic):
            payload = '%s'%chp + 'ff000100000000400c00' + g_tail
            self.write_by_hex(payload)
            time.sleep(0.02)
            payload = '%s'%chp + 'ff0001000000a0620c00' + g_tail
            self.write_by_hex(payload)
            time.sleep(0.02)
            payload = '%s'%chp + 'ff0001000000a0220400' + g_tail
            self.write_by_hex(payload)
            time.sleep(0.02)
            payload = '%s'%chp + 'ff0001000000a0220000' + g_tail
            self.write_by_hex(payload)
            ''' # Overdrive 10%
            payload = '%s'%chp + 'ff000100000000400c00' + g_tail
            self.write_by_hex(payload)
            time.sleep(0.02)
            payload = '%s'%chp + 'ff000100000060410c00' + g_tail
            self.write_by_hex(payload)
            time.sleep(0.02)
            payload = '%s'%chp + 'ff000100000060110400' + g_tail
            self.write_by_hex(payload)
            time.sleep(0.02)
            payload = '%s'%chp + 'ff000100000060110000' + g_tail
            self.write_by_hex(payload)
            '''
    def set_all_idle(self):
        payload = 'ffff0001000000a0220200' + g_tail
        self.write_by_hex(payload)

    def set_all_active(self):
        payload = 'ffff0001000000a0220000' + g_tail
        self.write_by_hex(payload) 

    def calc_asic_cores(self, scan):
        self.good_cores = 0
        self.bad_cores = 0

        if scan:
            for chp in sorted(self.asic):
                for clst in self.asic[chp]:
                    self.asic[chp][clst] = 0x0000
            for chp in sorted(self.asic):
                print 'Scanning ASIC %s...' % chp
                # set diagnosis mode
                payload = chp + 'ff0001000000a0220100' + g_tail
                self.write_by_hex(payload)
                # give golden sample work, expect 'ecff6386ebd9'
                # (chp | 0x80) only for diagnosis mode -- allow all answers get returned
                cc = '%02x' % (int(chp, 16) + 128)
                payload = cc + '0000000000000000000000000000000000000000000000000000a78e0100000001000000f615f7ce3b4fc6b8f61e8f89aedb1d0852507650533a9e3b10b9bbcc30639f279fcaa86746e1ef52d3edb3c4ad8259920d509bd073605c9bf1d59983752a6b06b817bb4ea78e011d012d59d4'
                self.write_by_hex(payload)
                cnt = 0
                while True:
                    resp = self.com_port.read(9)
                    if len(resp) == 9:
                        _chpid = resp[8].encode('hex')
                        if (_chpid > '1f'):
                            print 'chpid err!'
                        _clsid = resp[7].encode('hex')
                        if (_clsid > '05'):
                            print 'clsid err!'
                        _corid = ord(resp[6])
                        if (_corid > 8):
                            print 'corid err!'
                        _nonce = resp[3::-1].encode('hex')
                        #core_status = _nonce in 'ecff6386ebd9'
                        core_status = _nonce in '6386ebd9'
                        if core_status:
                            self.good_cores += 1
                            #print 'Good: %d, %d, %d' % (_chpid, _clsid, _corid)
                            self.asic[_chpid][_clsid] |= (1 << _corid)
                        else:
                            self.bad_cores += 1
                            print 'Bad: %s, %s, %s, %d' % (_nonce, _chpid, _clsid, _corid)

                        cnt = 0
                    cnt += 1
                    if (cnt > 5):
                        break
        else:
            #print self.asic
            for _chpid in self.asic:
                for _clsid in self.asic[_chpid]:
                    mask = 0x0100
                    while mask > 0:
                        if ((self.asic[_chpid][_clsid] & mask) != 0):
                            self.good_cores += 1
                        else:
                            self.bad_cores += 1
                        mask >>= 1

    def config_workspace(self, start_of_nonce, multiple):
        n_offset = start_of_nonce
        for chp in sorted(self.asic):
            # setup nonce incremental = 0x0001
            payload = ('%s' % chp) + 'ff0001000000a0220000' + g_tail
            time.sleep(0.01)
            self.write_by_hex(payload)

            for clst in sorted(self.asic[chp]):
                gc = 0
                offset = '%08x' % n_offset
                cores = '%04x' % self.asic[chp][clst]
                payload = '%sfe%s%s%s' % \
                          (chp, clst, \
                           offset.decode('hex')[::-1].encode('hex'), \
                           cores.decode('hex')[::-1].encode('hex')) + \
                          '00'*104
                self.write_by_hex(payload)
                #print '>>> %s' % payload
                core_mask = self.asic[chp][clst]
                for i in range(0, 15, 1):
                    if (core_mask & 0x0001):
                        gc += 1
                    core_mask >>= 1
                n_offset += multiple * gc


    def rev_per_4bytes(self, data):
        x = ''
        for i in range (0, len(data), 8):
            x += data[i+6:i+8] + data[i+4:i+6] + data[i+2:i+4] + data[i:i+2]
        return x

    def give_work(self, chip, target, block):
        header_hex = self.swap4(block[0:160])
        payload = chip + target + header_hex
        #self.write_by_hex(payload)
        return payload.decode('hex')[::-1]

    def swap4(self, binascii_str):
        str = binascii.unhexlify(binascii_str)
        x = len(str) / 4
        rev = ''.join([ str[i*4:i*4+4][::-1] for i in range(0, x) ])
        return binascii.hexlify(rev)

    def revall(self, binascii_str):
        str = binascii.unhexlify(binascii_str)
        rev = str[::-1]
        return binascii.hexlify(rev)



#------- hw.py --------

SUBMIT_Q_THROTTLE = 30
WEB_REFRESH_TIME = 5
LCM_REFRESH_TIME = 5
REFRESH_KHRATE_TIME = 5
STRATUM_CHK_INTERVAL = 30

rst = {'00':None, '01':None, '02':None, '03':None, '04':None, '05':None, '06':None, '07':None}
com = {'00':None, '01':None, '02':None, '03':None, '04':None, '05':None, '06':None, '07':None}
brd = {'00':None, '01':None, '02':None, '03':None, '04':None, '05':None, '06':None, '07':None}
pool_ctrl = {'00':None, '01':None, '02':None, '03':None, '04':None, '05':None, '06':None, '07':None}
alche_protocol = {'00':None, '01':None, '02':None, '03':None, '04':None, '05':None, '06':None, '07':None}
ans_queue = {'00':None, '01':None, '02':None, '03':None, '04':None, '05':None, '06':None, '07':None}

active_brd_num = 0
active_brd = []

miner_ctrl = Event()
for p in pool_ctrl:
    pool_ctrl[p] = Event()
submitter_ctrl = Event()
stat_reset = Event()

stratum_proxy_isRunning = False
ws_client = []

lcm = rdf022.get_lcm()
def lcm_disp(msg):
    msgs = ('IP:'+rdf022.get_ip(), msg)
    lcm.messages = msgs
    lcm.refresh()

class CoinRPC(object):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.url = 'http://' + self.host + ':' + self.port

    def reconnect(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password        
        self.url = 'http://' + self.host + ':' + self.port

    def getwork(self, data=None):
        payload = { 'version':'1.1', 'method':'getwork', 'params':[], 'id':'1' }

        payload['params'] = ([] if (data is None) else data)

        try:
            r = requests.post(self.url, \
                                auth=HTTPBasicAuth(self.username, self.password), \
                                data=json.dumps(payload), \
                                timeout=30)
            resp = r.json()
            if (resp['error'] is not None):
                print '-- RPC error!'
                print r.text
                return None
            else:
                return resp['result']

        except requests.ConnectionError:
            print '-- HTTP connection error!'
            return None

        except requests.Timeout:
            print '-- HTTP connection timeout!'
            return None

        except Exception as e:
            print '-- RPC general error!'
            print e
            return None

class Submitter(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.coin_rpc = CoinRPC(config.host, config.port, config.username, config.password)

    def run(self):
        while True:
            if submitter_ctrl.isSet():
                submitter_ctrl.clear()

            (bid, data, target, nonce_bin) = submit_queue.get()
            print '  -- Q (%d) --' % submit_queue.qsize()
            nonce = nonce_bin[::-1].encode('hex')
            solution = data[:152] + nonce + data[160:256]
            param_arr = [ solution ]

            submit_result = None
            for i in range(5):
                submit_result = self.coin_rpc.getwork(param_arr)
                if (submit_result is not None):
                    hash_queue.put((bid, submit_result, target, nonce_bin))
                    break
                else:
                    self.coin_rpc.reconnect(config.host, config.port, config.username, config.password)
                    print '** submit reconnect... **'
                    time.sleep(0.1)

            submit_queue.task_done()
            time.sleep(0.05)

class AlcheProtocol(LineReceiver):
    def __init__(self, bid):
        self.bid = bid
        self._busyReceiving = False
        self._buffer = b''

    def connectionMade(self):
        print self.bid + ' connected in AlcheProtocol.'
        #self.delimiter = b''

    def sendLine(self, line):
        return self.transport.write(line)

    def dataReceived(self, data):
        if self._busyReceiving:
            self._buffer += data
            return
        try:
            self._busyReceiving = True
            self._buffer += data
            while self._buffer and not self.paused:
                if (len(self._buffer) >= 9):
                    line = self._buffer[0:9]
                    self._buffer = self._buffer[9:]
                    why = self.ansReceived(line)
                    if (why or self.transport and self.transport.disconnecting):
                        return why
                else:
                    return
        finally:
            self._busyReceiving = False   

    def ansReceived(self, data):
        ans_queue[self.bid].put(data)

class Miner(Thread):
    def __init__(self, bid, board, arg_config, alcheprotocol):
        Thread.__init__(self)
        self.bid = bid
        self.daemon = True
        self.brd = board
        self.config = arg_config
        self.time_start = time.time()
        self.work_timeout = 3
        self.targetstr = ''
        self.diff = 1
        self.alche_protocol = alcheprotocol
        self.coin_rpc = CoinRPC(config.host, config.port, config.username, config.password)

    def do_work(self, datastr, targetstr):
        if (targetstr != self.targetstr):
            self.targetstr = targetstr
            self.diff = 0x0000ffff00000000 / long(targetstr[48:64].decode('hex')[::-1].encode('hex'), 16)
            #self.work_timeout = self.diff * 65536 / 1000000 / 32
            self.work_timeout = self.diff * 3.54 / brd[self.bid].good_cores
            if (self.work_timeout < 8):
                self.work_timeout = 8
        t = '0' * 48 + targetstr[48:64]
        payload = self.brd.give_work('ff', t, datastr)
        print '--(%s)-- diff: %0.2f, work_timeout: %0.2f' % (self.bid, self.diff, self.work_timeout)
        self.time_start = time.time()
        reactor.callFromThread(AlcheProtocol.sendLine, self.alche_protocol, payload)

        try:
            data = ans_queue[self.bid].get(timeout=self.work_timeout)
            dt = time.time() - self.time_start
            if (data == 'ffffffffffffffffff'):
                print '==(%s)== clean job! <%0.2f>' % (self.bid, dt)
                com_resp = ''
            else:
                print '==(%s)== %s <%0.2f>' % (self.bid, data.encode('hex'), dt)
                com_resp = data
        except Queue.Empty:
            com_resp = ''

        return com_resp[:4]

    def iterate(self):
        work = None
        for i in range(5):
            work = self.coin_rpc.getwork()
            if (work is not None):
                break
        if work is None:
            print 'ERR: Work is None'
            return False

        nonce_bin = self.do_work(work['data'], work['target'])

        if len(nonce_bin) == 4:
            submit_queue.put((self.bid, work['data'], work['target'], nonce_bin))
            if (submit_queue.qsize() > SUBMIT_Q_THROTTLE):
                print '...Nap for %0.2f sec...' % (active_brd_num * submit_queue.qsize() / SUBMIT_Q_THROTTLE)
                time.sleep(active_brd_num * submit_queue.qsize() / SUBMIT_Q_THROTTLE)

        return True

    def run(self):

        iterate_result = False

        while True:
            miner_ctrl.wait()
            if pool_ctrl[self.bid].isSet():
                iterate_result = False
                pool_ctrl[self.bid].clear()
            if (iterate_result == False):
                self.coin_rpc.reconnect(config.host, config.port, config.username, config.password)
            iterate_result = self.iterate()

class Stat(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.acc_kh = {'00':0.00, '01':0.00, '02':0.00, '03':0.00, '04':0.00, '05':0.00, '06':0.00, '07':0.00}
        self.khrate = {'00':0.00, '01':0.00, '02':0.00, '03':0.00, '04':0.00, '05':0.00, '06':0.00, '07':0.00, 'accepted':0, 'rejected':0, 'since':0}
        self.total_accepted = 0
        self.total_rejected = 0
        self.miner_stt_time = time.time()
        self.reset_stt_time()

    def reset_stt_time(self):
        self.miner_stt_time = time.time()
        self.khrate['since'] = self.miner_stt_time

    def reset_stat(self):
        for b in ['00', '01', '02', '03', '04', '05', '06', '07']:
            self.acc_kh[b] = 0.00
            self.khrate[b] = 0.00
        self.khrate['accepted'] = 0
        self.khrate['rejected'] = 0
        self.total_accepted = 0
        self.total_rejected = 0
        self.reset_stt_time()

    def refresh_khrate(self):
        for i in ['00', '01', '02', '03', '04', '05', '06', '07']:
            self.khrate[i] = self.acc_kh[i] / (time.time() - self.miner_stt_time)

    def run(self):
        while True:
            (bid, sr, tgt, nnc_bin) = hash_queue.get()

            diff = 0x0000ffff00000000 / long(tgt[48:64].decode('hex')[::-1].encode('hex'), 16)
            _acc_kh = self.acc_kh[bid]
            _acc_kh += diff * 65.536 * 1
            self.acc_kh[bid] = _acc_kh
            self.khrate[bid] = _acc_kh / (time.time() - self.miner_stt_time)

            if sr:
                self.total_accepted += 1
                self.khrate['accepted'] = self.total_accepted
            else:
                self.total_rejected += 1
                self.khrate['rejected'] = self.total_rejected

            hash_queue.task_done()




class StratumProxy(object):
    def __init__(self):
        self.proxy = None
        self.isRunning = False
        self.stratum_host = None
        self.stratum_port = None

    def get_params(self):
        return (self.stratum_host, self.stratum_port)

    def start(self, stratum_host, stratum_port, getwork_port, username, password):
        self.stratum_host = stratum_host
        self.stratum_port = stratum_port

        if not self.isRunning:
            if ('ghash.io' in stratum_host):
                self.proxy = subprocess.Popen(['/usr/bin/python', 'stratum-mining-proxy/mining_proxy.py', \
                                                '-o', stratum_host, '-p', stratum_port, '-gp', getwork_port , \
                                                '-cu', username, '-cp', password, '-pa', 'scrypt', \
                                                '-nm', '-q'], stdout=subprocess.PIPE, shell=False)
            else:
                self.proxy = subprocess.Popen(['/usr/bin/python', 'stratum-mining-proxy/mining_proxy.py', \
                                                '-o', stratum_host, '-p', stratum_port, '-gp', getwork_port , \
                                                '-cu', username, '-cp', password, '-pa', 'scrypt', \
                                                '-nm', '-cd', '-q'], stdout=subprocess.PIPE, shell=False)
            self.isRunning = True

    def stop(self):
        if self.isRunning:
            self.proxy.kill()
            os.wait()
            self.isRunning = False


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
            # Reset stat
            stat.reset_stat()

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
            stratum_mtr.stop()
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

                # Reset stat
                stat.reset_stat()

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
            stratum_mtr.start(STRATUM_CHK_INTERVAL)

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
        # clear submit_queue
        while not submit_queue.empty():
            try:
                submit_queue.get(False)
            except Queue.Empty:
                continue
            submit_queue.task_done()

        return

lcm_disp('Hello, miner...')

def refresh_khrate():
    stat.refresh_khrate()

def web_display():
    rsp = {'result':stat.khrate, 'error':None, 'id':'s1'}
    for i in ws_client:
        reactor.callFromThread(WebSocketServerProtocol.sendMessage, i, json.dumps(rsp))

def lcm_display():
    total_khashrate = 0
    for i in ['00', '01', '02', '03', '04', '05', '06', '07']:
        total_khashrate += stat.khrate[i]
        #print '-- Total hash rate: %0.2f' % total_khashrate
        #print '-- Total submit: accepted (%d), rejected (%d)' % (self.total_accepted, self.total_rejected)
    lcm_disp('HR: %0.2f Mh/s' % (total_khashrate/1000))

def stratum_monitor():
    '''
    if (config.protocol == 'stratum+tcp:'):
        print '..check stratum proxy..'
        retry = 0
        while (retry < 10):    
            s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex(('127.0.0.1', 8332))
            s.close()
            if result > 0:
                retry += 1
            else:
                break
        if (retry >= 10):
            print 'Restarting stratum proxy...'
            stratum_proxy.stop()
            time.sleep(3)
            stratum_proxy.start(stratum_host, stratum_port, config.port, config.username, config.password)
    '''
    test_payload = { 'version':'1.1', 'method':'getwork', 'params':[], 'id':'mtr' }
    test_data = json.dumps(test_payload)
    if (config.protocol == 'stratum+tcp:'):
        print '...check stratum proxy...'
        retry = 0
        while (retry < 10):
            try:
                r = requests.post('http://localhost:8332', \
                                    auth=HTTPBasicAuth(config.username, config.password), \
                                    data=test_data, \
                                    timeout=30)
                resp = r.json()
                if (resp['error'] is not None):
                    print '-- (stratum_monitor) RPC error!'
                    retry += 1
                else:
                    break
            except requests.ConnectionError:
                print '-- (stratum_monitor) HTTP connection error!'
                retry += 1
            except requests.Timeout:
                print '-- (stratum_monitor) HTTP connection timeout!'
                retry += 1
            except Exception as e:
                print '-- (stratum_monitor) RPC general error!'
                retry += 1

        if (retry >= 10):
            (stratum_host, stratum_port) = stratum_proxy.get_params()
            print 'Restarting stratum proxy...'
            stratum_proxy.stop()
            time.sleep(3)
            stratum_proxy.start(stratum_host, stratum_port, config.port, config.username, config.password)
         
def enable_miners():
    miner_ctrl.set()
    stratum_mtr.start(STRATUM_CHK_INTERVAL)

if __name__ == '__main__':


    for b in alche_protocol:
        alche_protocol[b] = AlcheProtocol(b)

    stratum_proxy = StratumProxy()

    factory = WebSocketServerFactory('ws://127.0.0.1:9000', debug=True)
    factory.protocol = WebUIProtocol
    reactor.listenTCP(9000, factory)

    total_accepted = 0
    total_rejected = 0

    for b in ans_queue:
        ans_queue[b] = Queue.Queue()
    submit_queue = Queue.Queue()
    hash_queue = Queue.Queue()

    # Initialize mandatory config parameters
    print 'Reading config.ini...'
    if os.path.isfile('config.ini'):
        config = ArgsConfig('config.ini')
        config.read_config()
    else:
        print 'config.ini does exist!'
        sys.exit()

    rst['00'] = config.p0_reset
    rst['01'] = config.p1_reset
    rst['02'] = config.p2_reset
    rst['03'] = config.p3_reset
    rst['04'] = config.p4_reset
    rst['05'] = config.p5_reset
    rst['06'] = config.p6_reset
    rst['07'] = config.p7_reset

    print 'Opening serial ports...'
    com['00'] = Serial(config.p0_com, 115200, timeout=0.01)
    com['01'] = Serial(config.p1_com, 115200, timeout=0.01)
    com['02'] = Serial(config.p2_com, 115200, timeout=0.01)
    com['03'] = Serial(config.p3_com, 115200, timeout=0.01)
    com['04'] = Serial(config.p4_com, 115200, timeout=0.01)
    com['05'] = Serial(config.p5_com, 115200, timeout=0.01)
    com['06'] = Serial(config.p6_com, 115200, timeout=0.01)
    com['07'] = Serial(config.p7_com, 115200, timeout=0.01)

    # Initialize AsicBoard and do reset
    print 'Initializing boards (reset, flush, setup PLL)...'
    for b in sorted(brd):
        brd[b] = AsicBoard(com[b], rst[b], alche_protocol[b])
        brd[b].reset()
        brd[b].set_pll()

    # Read default ASIC resources
    asic_state = AsicConfig('asic.ini')
    if (os.path.isfile('asic.ini') and (config.force_diag != 'yes')):
        print 'Reading asic.ini...'
        asic_state.read_config()
        #print brd
        for b in sorted(brd):
            for chp in sorted(brd[b].asic):
                for clst in sorted((brd[b].asic)[chp]):
                    (brd[b].asic)[chp][clst] = asic_state.asic_rsc[b][chp][clst]
            brd[b].calc_asic_cores(scan=False)
    else:
        # Scan ASIC resources
        print 'Scanning ASIC resources...'
        for b in sorted(brd):
            print 'Board: ' + b
            brd[b].calc_asic_cores(scan=True)
            for chp in sorted(brd[b].asic):
                for clst in sorted((brd[b].asic)[chp]):
                    asic_state.asic_rsc[b][chp][clst] = (brd[b].asic)[chp][clst]
        asic_state.save_config()

    # Close all serial ports
    for b in com:
        com[b].close()

    com['00'] = SerialPort(alche_protocol['00'], config.p0_com, reactor, baudrate=115200)
    com['01'] = SerialPort(alche_protocol['01'], config.p1_com, reactor, baudrate=115200)
    com['02'] = SerialPort(alche_protocol['02'], config.p2_com, reactor, baudrate=115200)
    com['03'] = SerialPort(alche_protocol['03'], config.p3_com, reactor, baudrate=115200)
    com['04'] = SerialPort(alche_protocol['04'], config.p4_com, reactor, baudrate=115200)
    com['05'] = SerialPort(alche_protocol['05'], config.p5_com, reactor, baudrate=115200)
    com['06'] = SerialPort(alche_protocol['06'], config.p6_com, reactor, baudrate=115200)
    com['07'] = SerialPort(alche_protocol['07'], config.p7_com, reactor, baudrate=115200)

    print 'Re-initializing boards (reset, setup PLL)...'
    for b in sorted(brd):
        brd[b].set_comport_async_mode()
        brd[b].reset()
        brd[b].set_pll()

    # Config work space
    print 'Configuring work space...'
    active_brd_num = 0
    active_brd = []
    for b in sorted(brd):
        print 'looking for good_cores board: ' + b
        if (brd[b].good_cores != 0):
            print 'board %s has %d good_cores and %d bad_cores' % (b, brd[b].good_cores, brd[b].bad_cores)
            brd[b].config_workspace(0x00000000, 2**32/brd[b].good_cores)
            active_brd.append(b)
            active_brd_num += 1


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
        # startup minter threads after 5 sec...
        reactor.callLater(8, enable_miners)

    sm = Submitter()
    sm.start()

    print active_brd



    thr_list = []
    for thr_id in sorted(active_brd):
        t = Miner(thr_id, brd[thr_id], config, alche_protocol[thr_id])
        t.start()
        thr_list.append(t)

    #time.sleep(1)
    stat = Stat()
    stat.start()
    
    print time.asctime() + ' Miner Starts ..'
    stat.reset_stt_time()

    webdisp = LoopingCall(web_display)
    webdisp.start(WEB_REFRESH_TIME)
    lcmdisp = LoopingCall(lcm_display)
    lcmdisp.start(LCM_REFRESH_TIME)
    refkh = LoopingCall(refresh_khrate)
    refkh.start(REFRESH_KHRATE_TIME)

    #print 'Thread created:'
    #print thr_list

    stratum_mtr = LoopingCall(stratum_monitor)

    reactor.run()

    print '\nResetting boards ...'
    for b in sorted(brd):
        brd[b].reset()

    print time.asctime() + 'Miner Stop.'
