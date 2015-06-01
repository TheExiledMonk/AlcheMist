import json
import ConfigParser
#from ConfigParser import SafeConfigParser, ConfigParser

MAX_BOARDS = 8
MAX_CHIPS = 32
MAX_CLUSTERS = 6
MAX_CORES = 9

class ArgsConfig(object):

    def __init__(self, filename):

        self.filename = filename
        self.config = ConfigParser.SafeConfigParser()
        #self.config.read(self.filename)
        self.protocol = None
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.immediately_run = False
        self.force_diag = False
        self.p0_reset = 'gpio117'
        self.p1_reset = 'gpio110'
        self.p2_reset = 'gpio111'
        self.p3_reset = 'gpio112'
        self.p4_reset = 'gpio113'
        self.p5_reset = 'gpio114'
        self.p6_reset = 'gpio115'
        self.p7_reset = 'gpio116'
        self.p0_com = '/dev/ttyO1'
        self.p1_com = '/dev/ttyO2'
        self.p2_com = '/dev/ttyO3'
        self.p3_com = '/dev/ttyO4'
        self.p4_com = '/dev/ttyUSB0'
        self.p5_com = '/dev/ttyUSB1'
        self.p6_com = '/dev/ttyUSB2'
        self.p7_com = '/dev/ttyUSB3'

    def read_config(self):

        #self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.filename)

        for candidate in ['pool', 'hardware']:
            if self.config.has_section(candidate) is False:
                print '[%s] section does not exist!' % candidate
                return False
        for candidate in ['protocol', 'host', 'port', 'username', 'password', 'immediately_run', 'force_diag']:
            if self.config.has_option('pool', candidate) is False:
                print '\'%s\' does not exist in section [%s]!' % (candidate, 'pool')
                return False
        for candidate in ['p0_reset', 'p1_reset', 'p2_reset', 'p3_reset', \
                          'p4_reset', 'p5_reset', 'p6_reset', 'p7_reset', \
                          'p0_com', 'p1_com', 'p2_com', 'p3_com', \
                          'p4_com', 'p5_com', 'p6_com', 'p7_com']:
            if self.config.has_option('hardware', candidate) is False:
                print 'Errors in [hardware] section!'
                return False

        self.protocol = self.config.get('pool', 'protocol')
        self.host = self.config.get('pool', 'host')
        self.port = self.config.get('pool', 'port')
        self.username = self.config.get('pool', 'username')
        self.password = self.config.get('pool', 'password')
        self.immediately_run = self.config.get('pool', 'immediately_run')
        self.force_diag = self.config.get('pool', 'force_diag')

        self.p0_reset = self.config.get('hardware', 'p0_reset')
        self.p0_com = self.config.get('hardware', 'p0_com')
        self.p1_reset = self.config.get('hardware', 'p1_reset')
        self.p1_com = self.config.get('hardware', 'p1_com')
        self.p2_reset = self.config.get('hardware', 'p2_reset')
        self.p2_com = self.config.get('hardware', 'p2_com')
        self.p3_reset = self.config.get('hardware', 'p3_reset')
        self.p3_com = self.config.get('hardware', 'p3_com')
        self.p4_reset = self.config.get('hardware', 'p4_reset')
        self.p4_com = self.config.get('hardware', 'p4_com')
        self.p5_reset = self.config.get('hardware', 'p5_reset')
        self.p5_com = self.config.get('hardware', 'p5_com')
        self.p6_reset = self.config.get('hardware', 'p6_reset')
        self.p6_com = self.config.get('hardware', 'p6_com')
        self.p7_reset = self.config.get('hardware', 'p7_reset')
        self.p7_com = self.config.get('hardware', 'p7_com')

        return True

    def save_config(self):

        self.config.set('pool', 'protocol', self.protocol)
        self.config.set('pool', 'host', self.host)
        self.config.set('pool', 'port', self.port)
        self.config.set('pool', 'username', self.username)
        self.config.set('pool', 'password', self.password)
        self.config.set('pool', 'immediately_run', self.immediately_run)
        self.config.set('pool', 'force_diag', self.force_diag)

        try:
            f = open(self.filename, 'w+')
            self.config.write(f)
            f.close()
        except IOError:
            print 'Write %s fail!' % self.filename
            return False

        return True

class AsicConfig(object):

    def __init__(self, filename):

        self.filename = filename
        self.config = ConfigParser.SafeConfigParser()
        self.config.read(self.filename)
        self.asic_rsc = {}

        for i in range(MAX_BOARDS):
            self.asic_rsc['%02x'%i] = {}
            for j in range(MAX_CHIPS):
                self.asic_rsc['%02x'%i]['%02x'%j] = {}
                for k in range(MAX_CLUSTERS):
                    self.asic_rsc['%02x'%i]['%02x'%j]['%02x'%k] = 0x0000

    def read_config(self):

        for i in range(MAX_BOARDS):
            for j in range(MAX_CHIPS):
                try:
                    rsc = self.config.get('board_%02x'%i, 'asic_%02x'%j)
                    self.asic_rsc['%02x'%i]['%02x'%j] = json.loads(rsc)
                    #except SafeConfigParser.NoSectionError, SafeConfigParser.NoOptionError:
                except Exception:
                    pass
        return

    def save_config(self):

        for i in range(MAX_BOARDS):
            for j in range(MAX_CHIPS):
                rsc = self.asic_rsc['%02x'%i]['%02x'%j]
                if self.config.has_section('board_%02x'%i) is False:
                    self.config.add_section('board_%02x'%i)
                self.config.set('board_%02x'%i, 'asic_%02x'%j, json.dumps(rsc))

        try:
            f = open(self.filename, 'w+')
            self.config.write(f)
            f.close()
        except IOError:
            print 'Write %s fail!' % self.filename
            return False

        return True

