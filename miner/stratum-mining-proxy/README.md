stratum-mining-proxy
====================

This is a fork of Slush's Stratum mining proxy, adapted for Litecoin mining.
Some deprecated features only required by very old Bitcoin miners, such as midstate, have also been removed.

Installation on Windows
-----------------------

1. Download official Windows binaries (EXE) from https://www.litecoinpool.org/files/mining_proxy.exe
2. Open downloaded file. It will open a console window. Using default settings, proxy connects to litecoinpool.org
3. If you want to connect to another pool or change other proxy settings, type "mining_proxy.exe --help" in console window.

Installation on Linux
---------------------

1. Download TGZ file from https://github.com/pooler/stratum-mining-proxy/tarball/master
2. Unpack it by typing "tar xf pooler-stratum-mining_proxy*.tar.gz"
3. Most likely you already have Python installed on your system. Otherwise install it by "sudo apt-get install python-dev"
(on Ubuntu and Debian).
3. Type "sudo python setup.py install" in the unpacked directory.
4. You can start the proxy by typing "./mining_proxy.py" in the terminal window. Using default settings,
proxy connects to litecoinpool.org.
5. If you want to connect to another pool or change other proxy settings, type "mining_proxy.py --help".

Installation on Mac
-------------------
1. Download TGZ file from https://github.com/pooler/stratum-mining-proxy/tarball/master
2. Unpack it by typing "tar xf pooler-stratum-mining-proxy*.tar.gz"
3. On Mac OS X you already have Python installed on your system, but you lack the llvm-gcc-4.2 binary required to run the setup.py file, so:
3. a) If you don't want to install Xcode, get gcc here: https://github.com/kennethreitz/osx-gcc-installer
3. b) OR download Xcode (free) from the App Store, Open it up (it's in your applications folder) and go to preferences, to the downloads section and download/install the 'command line tools'. This will install llvm-gc-4.2.
4. Type "sudo python setup.py install" in the unpacked directory from step 2.
5. You can start the proxy by typing "./mining_proxy.py" in the terminal window. Using default settings, proxy connects to litecoinpool.org.
6. If you want to connect to another pool or change other proxy settings, type "mining_proxy.py --help".

N.B. Once Apple releases Xcode 4.7 they will remove the optional install of gcc (they want you to use clang). When that happens you can either choose not to upgrade, or return to the aforementioned https://github.com/kennethreitz/osx-gcc-installer and download the specific gcc binary for your version of Mac OS.

Installation on Linux using Git
-------------------------------
This is an advanced option for experienced users, but gives you the easiest way for updating the proxy.

1. git clone git://github.com/pooler/stratum-mining-proxy.git
2. cd stratum-mining-proxy
3. sudo apt-get install python-dev # Development package of Python are necessary
4. sudo python distribute_setup.py # This will upgrade setuptools package
5. sudo python setup.py develop # This will install required dependencies (namely Twisted and Stratum libraries),
but don't install the package into the system.
6. You can start the proxy by typing "./mining_proxy.py" in the terminal window. Using default settings,
proxy connects to litecoinpool.org.
7. If you want to connect to another pool or change other proxy settings, type "./mining_proxy.py --help".
8. If you want to update the proxy, type "git pull" in the package directory.

Contact
-------

This proxy is provided by Slush's mining pool at http://mining.bitcoin.cz. You can contact the author
by email info(at)bitcoin.cz or by IRC on irc.freenode.net in channel #stratum.
