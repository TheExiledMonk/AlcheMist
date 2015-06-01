from serial import Serial
import subprocess
from time import sleep
import binascii

MAX_BOARDS = 8
MAX_CHIPS = 32
MAX_CLUSTERS = 6
MAX_CORES = 9

g_tail = '00000000000000000000000000000000a78e0100000001000000f615f7ce3b4fc6b8f61e8f89aedb1d0852507650533a9e3b10b9bbcc30639f279fcaa86746e1ef52d3edb3c4ad8259920d509bd073605c9bf1d59983752a6b06b817bb4ea78e011d012d59d4'

class AsicBoard(object):

    def __init__(self, com_port, reset_gpio):
        self.com_port = com_port
        self.reset_gpio = reset_gpio
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

    def write_by_hex(self, data):
        self.com_port.write(data.decode('hex')[::-1])

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
            payload = '%s'%chp + 'ff0001000000a0620c00' + g_tail
            self.write_by_hex(payload)
            payload = '%s'%chp + 'ff0001000000a0220400' + g_tail
            self.write_by_hex(payload)
            payload = '%s'%chp + 'ff0001000000a0220000' + g_tail
            self.write_by_hex(payload)

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
            sleep(0.1)
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


