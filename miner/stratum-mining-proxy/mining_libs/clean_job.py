from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
import json

import stratum.logger
log = stratum.logger.get_logger('proxy')

class CleanJobProtocol(WebSocketClientProtocol):

   def onConnect(self, response):
      log.warn("Clean Job channel connected.")

   def onOpen(self):
      log.warn("Clean Job channel connection open.")

   def onMessage(self, payload, isBinary):
      log.warn("%s" % payload)

   def onClose(self, wasClean, code, reason):
      log.warn("Clean Job channel closed.")

   @classmethod
   def send_clean_job_msg(cls):
      rpc_tx = {"method":"clean_job","params":[],"id":"cj"}
      cls.sendMessage(json.dumps(rpc_tx))