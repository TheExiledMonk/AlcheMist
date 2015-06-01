#! /usr/bin/python

import cgi, os
import cgitb; cgitb.enable()
import subprocess

form = cgi.FieldStorage()

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
   while True:
      chunk = f.read(chunk_size)
      if not chunk: break
      yield chunk

def show_msg(s):
  print '''Content-Type: text/html\n\n<html><body><p>%s</p></body></html>''' % (s,)

# A nested FieldStorage instance holds the file
fileitem = form['filename']

# Test if the file was uploaded
if fileitem.filename:
    # strip leading path from file name to avoid directory traversal attacks
    fn = os.path.basename(fileitem.filename)
    f = open('/tmp/' + fn, 'wb', 10000)

    # Read the file in chunks
    for chunk in fbuffer(fileitem.file):
      f.write(chunk)
    f.close()

    message = 'The file "' + fn + '" was uploaded successfully.<br>Miner software is upgrading...'
    show_msg(message)

    xupg = subprocess.call(['/bin/tar', 'xzC', '/tmp', '-f', '/tmp/'+fn], shell=False)
    if (xupg == 0):
      doupg = subprocess.Popen(['/bin/sh','/tmp/AlcheMist/do-upgrade'], stdout=subprocess.PIPE, shell=False)
      for line in doupg.stdout:
        print line
      doupg.wait()
      if (doupg.returncode == 0):
        print 'Done. Miner is rebooting...'
      else:
        print 'Wrong software package!'
    else:
      print 'File format error!'
else:
   message = 'No file was uploaded!'
   show_msg(message)



